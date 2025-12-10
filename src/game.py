import pandas as pd
from typing import List, Dict, Optional, Tuple
from importlib import invalidate_caches
import streamlit as st

from utils import (
    get_client,
    get_player_id,
    get_player_name,
    calcul_delta_elo,
    get_player_elo,
    get_player_rank,
    get_delta_elo
)


class GameConfig:
    """Configuration centralisée du jeu"""
    URL_SIMPLE = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/simple.png"
    URL_DOUBLE = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/double.png"
    URL_TRIPLE = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/triple.png"
    URL_BLANK = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/blank.png"

    DARTS_PER_ROUND = 3
    NUM_ROUNDS = 20
    TARGETS = ["20", "19", "18", "17", "16", "15", "25"]
    TARGETS_DISPLAY = ["20", "19", "18", "17", "16", "15", "B"]
    MAX_SCORE_PER_TARGET = 3


def get_icon(score: int) -> str:
    """
    Retourne l'URL de l'icône correspondant au score.
    
    Args:
        score: Score du joueur sur une cible (0-3)
        
    Returns:
        URL de l'icône correspondante
    """
    icon_map = {
        3: GameConfig.URL_TRIPLE,
        2: GameConfig.URL_DOUBLE,
        1: GameConfig.URL_SIMPLE
    }
    return icon_map.get(score, GameConfig.URL_BLANK)


def create_match_in_db() -> Optional[int]:
    """
    Crée un nouveau match dans la base de données.
    
    Returns:
        ID du match créé, ou None en cas d'erreur
        
    Raises:
        Exception: En cas d'erreur lors de la création
    """
    client = get_client()
    try:
        response = client.table("matches").insert(
            [{"is_finished": False}], count="None"
        ).execute()
        return response.data[0]['id']
    except Exception as e:
        st.error(f"Erreur lors de la création du match : {e}")
        raise


def get_state_from_db(match_id: int) -> Tuple[pd.DataFrame, List[str]]:
    """
    Récupère l'état d'un match depuis la base de données.
    
    Args:
        match_id: ID du match à récupérer
        
    Returns:
        Tuple contenant (état du jeu, liste des joueurs)
    """
    client = get_client()
    response_match_state = (
        client.table("match_state")
        .select("player_id", "target", "score")
        .eq("match_id", match_id)
        .execute()
    )

    player_ids = list({item["player_id"] for item in response_match_state.data})
    player_list = [get_player_name(int(player_id)) for player_id in player_ids]

    state = pd.DataFrame(
        [{name: 0 for name in player_list} for _ in range(len(GameConfig.TARGETS))],
        index=GameConfig.TARGETS
    )

    for data in response_match_state.data:
        state.loc[data["target"], get_player_name(int(data["player_id"]))] = data["score"]

    return state, player_list


def get_points_from_db(match_id: int, player_list: List[str]) -> pd.DataFrame:
    """
    Récupère les points des joueurs depuis la base de données.
    
    Args:
        match_id: ID du match
        player_list: Liste des noms de joueurs
        
    Returns:
        DataFrame contenant les points des joueurs
    """
    client = get_client()
    response_player_points = (
        client.table("match_points")
        .select("player_id", "points")
        .eq("match_id", match_id)
        .execute()
    )

    player_points = pd.DataFrame(
        [{name: 0 for name in player_list}],
        index=["points"]
    )

    for data in response_player_points.data:
        player_points.loc["points", get_player_name(int(data["player_id"]))] = data["points"]

    return player_points


class CricketGame:
    """
    Classe représentant une partie de Cricket (jeu de fléchettes).
    
    Attributes:
        id_match: ID unique du match
        player_list: Liste des noms des joueurs
        actual_state: État actuel du jeu (scores par cible)
        player_points: Points actuels des joueurs
        match_ended: Indicateur de fin de match
    """

    def __init__(self, player_list: Optional[List[str]] = None, match_id: Optional[int] = None):
        """
        Initialise une nouvelle partie ou charge une partie existante.
        
        Args:
            player_list: Liste des joueurs pour une nouvelle partie
            match_id: ID d'un match existant à charger
        """
        if player_list:
            self._init_new_game(player_list)
        elif match_id:
            self._load_existing_game(match_id)
        else:
            raise ValueError("Vous devez fournir soit player_list, soit match_id")

    def _init_new_game(self, player_list: List[str]) -> None:
        """Initialise une nouvelle partie."""
        self.id_match = create_match_in_db()
        self.player_list = player_list
        self.multi = 1
        self.total_dart_number = (
                len(player_list) * GameConfig.DARTS_PER_ROUND * GameConfig.NUM_ROUNDS
        )
        self.actual_dart = 1

        self.actual_state = pd.DataFrame(
            [{name: 0 for name in player_list} for _ in range(len(GameConfig.TARGETS))],
            index=GameConfig.TARGETS
        )

        self.player_points = pd.DataFrame(
            [{name: 0 for name in player_list}],
            index=["points"]
        )

        self.state_history: Dict[str, pd.DataFrame] = {}
        self.points_history: Dict[str, pd.DataFrame] = {}

        self.match_ended = False

    def _load_existing_game(self, match_id: int) -> None:
        """Charge une partie existante depuis la base de données."""
        self.id_match = match_id
        self.actual_state, self.player_list = get_state_from_db(match_id)
        self.player_points = get_points_from_db(match_id, self.player_list)
        self.match_ended = True

    def get_actual_player(self) -> str:
        """Retourne le nom du joueur actuel."""
        player_index = ((self.actual_dart - 1) // GameConfig.DARTS_PER_ROUND) % len(self.player_list)
        return self.player_list[player_index]

    def get_tour_number(self) -> int:
        """Retourne le numéro du tour actuel."""
        if self.match_ended:
            return GameConfig.NUM_ROUNDS
        return (self.actual_dart - 1) // (len(self.player_list) * GameConfig.DARTS_PER_ROUND) + 1

    def get_num_remaining_darts(self) -> int:
        """Retourne le nombre de fléchettes restantes dans le tour."""
        if self.match_ended:
            return 0
        return GameConfig.DARTS_PER_ROUND - ((self.actual_dart - 1) % GameConfig.DARTS_PER_ROUND)

    def get_cell(self, player: str, target: str) -> int:
        """Retourne le score d'un joueur sur une cible."""
        return int(self.actual_state.loc[target, player])

    def get_points(self, player: str) -> int:
        """Retourne les points d'un joueur."""
        return int(self.player_points.loc["points", player])

    def get_ranking(self) -> Dict[str, List[str]]:
        """
        Retourne le classement actuel des joueurs.
        
        Returns:
            Dictionnaire {rang : [liste de joueurs]}
            Exemple : {"1" : ["Alice"], "2" : ["Bob", "Tom"]}
        """
        sorted_players = self.player_points.loc["points"].sort_values()

        ranking = {}
        current_rank = 1
        previous_score = None

        for player, score in sorted_players.items():
            if score != previous_score:
                ranking[str(current_rank)] = [player]
                previous_score = score
                current_rank += 1
            else:
                ranking[str(current_rank - 1)].append(player)

        return ranking

    def get_ranking_to_print(self, for_history: bool = False) -> str:
        """
        Génère une représentation HTML du classement avec les deltas ELO.
        
        Args:
            for_history: Si True, n'affiche pas l'ELO actuel
            
        Returns:
            Chaîne HTML formatée du classement
        """
        player_ranking = self.get_ranking()
        medals = ["🥇", "🥈", "🥉"]
        ranks = medals + [str(i) for i in range(4, len(player_ranking) + 1)]

        result_lines = []

        for rank, (rank_key, players) in zip(ranks, player_ranking.items()):
            players_formatted = []

            for player in players:
                delta = get_delta_elo(self.id_match, player)
                sign_delta = f"{delta:+}"
                color = "green" if delta >= 0 else "red"

                elo_display = "" if for_history else f"{get_player_elo(player)} "
                player_str = f"{player} {elo_display}<span style='color:{color}'>({sign_delta})</span>"
                players_formatted.append(player_str)

            result_lines.append(f"{rank}: {', '.join(players_formatted)}")

        return "  \n".join(result_lines)

    def get_df_to_print(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Retourne les DataFrames formatés pour l'affichage Streamlit.
        
        Returns:
            Tuple (DataFrame avec icônes, DataFrame des points)
        """
        df_with_icons = pd.DataFrame(
            {
                player: [get_icon(self.get_cell(player, target)) for target in GameConfig.TARGETS]
                for player in self.player_list
            },
            index=GameConfig.TARGETS_DISPLAY,
            dtype=object
        )

        return df_with_icons, self.player_points

    def set_multi(self, multiplier: int) -> None:
        """Définit le multiplicateur pour le prochain lancer."""
        if multiplier in [1, 2, 3]:
            self.multi = multiplier
        else:
            raise ValueError("Le multiplicateur doit être 1, 2 ou 3")

    def is_player_winning(self, player: str) -> bool:
        """
        Vérifie si un joueur a gagné (toutes les cibles à 3 et le moins de points).
        
        Args:
            player: Nom du joueur à vérifier
            
        Returns:
            True si le joueur a gagné, False sinon
        """
        if self.actual_state.loc[:, player].tolist() != [GameConfig.MAX_SCORE_PER_TARGET] * len(GameConfig.TARGETS):
            return False

        player_score = self.get_points(player)
        for other_player in self.player_list:
            if other_player != player:
                if self.get_points(other_player) <= player_score:
                    return False

        return True

    def check_end_match(self) -> bool:
        """Vérifie si le match est terminé."""
        if self.actual_dart > self.total_dart_number:
            return True

        return any(self.is_player_winning(player) for player in self.player_list)

    def throw(self, target: str) -> None:
        """
        Effectue un lancer sur une cible.
        
        Args:
            target: Cible visée ("20", "19", ..., "25", ou "0" pour raté)
        """
        if self.match_ended:
            return

        self.state_history[str(self.actual_dart)] = self.actual_state.copy()
        self.points_history[str(self.actual_dart)] = self.player_points.copy()

        actual_player = self.get_actual_player()

        if target != "0":
            current_score = self.get_cell(actual_player, target)
            new_score = current_score + self.multi

            if new_score > GameConfig.MAX_SCORE_PER_TARGET:
                overflow = new_score - GameConfig.MAX_SCORE_PER_TARGET
                added_points = overflow * int(target)

                for other_player in self.player_list:
                    if other_player != actual_player and self.get_cell(other_player,
                                                                       target) < GameConfig.MAX_SCORE_PER_TARGET:
                        self.player_points.loc["points", other_player] += added_points

            self.actual_state.loc[target, actual_player] = min(new_score, GameConfig.MAX_SCORE_PER_TARGET)

        self.multi = 1
        self.actual_dart += 1
        self.match_ended = self.check_end_match()

    def return_to_last_state(self) -> None:
        """Annule le dernier lancer."""
        prev_dart_key = str(self.actual_dart - 1)

        if prev_dart_key in self.state_history:
            self.actual_state = self.state_history[prev_dart_key]
            self.player_points = self.points_history[prev_dart_key]
            self.actual_dart -= 1
            self.match_ended = False

    def state_to_base(self) -> None:
        """
        Sauvegarde l'état complet du match dans la base de données.
        Optimisé avec des insertions groupées (batch inserts).
        
        Raises:
            Exception: En cas d'erreur lors de la sauvegarde
        """
        client = get_client()

        match_points_data = []
        match_state_data = []
        match_ranking_data = []
        player_updates = []

        players_ranking = self.get_ranking()
        deltas_elo = calcul_delta_elo(players_ranking, self.player_list)

        for player in self.player_list:
            player_id = get_player_id(player)

            match_points_data.append({
                "match_id": self.id_match,
                "player_id": player_id,
                "points": int(self.get_points(player)),
            })

            for target in GameConfig.TARGETS:
                match_state_data.append({
                    "match_id": self.id_match,
                    "player_id": player_id,
                    "target": target,
                    "score": int(self.get_cell(player, target))
                })

            old_elo = get_player_elo(player)
            delta_elo = deltas_elo[player]
            new_elo = old_elo + delta_elo

            match_ranking_data.append({
                "match_id": self.id_match,
                "player_id": player_id,
                "rank": get_player_rank(players_ranking, player),
                "old_elo": old_elo,
                "new_elo": new_elo,
                "delta_elo": delta_elo
            })

            player_updates.append({"id": player_id, "elo": new_elo})

        try:
            if match_points_data:
                client.table("match_points").insert(match_points_data, count="None").execute()

            if match_state_data:
                client.table("match_state").insert(match_state_data, count="None").execute()

            if match_ranking_data:
                client.table("match_ranking").insert(match_ranking_data, count="None").execute()

            client.table("matches").update({"is_finished": True}).eq("id", self.id_match).execute()

            for update in player_updates:
                client.table("players").update({"player_elo": update["elo"]}).eq("id", update["id"]).execute()

            invalidate_caches()

            st.success("Match sauvegardé avec succès!")

        except Exception as e:
            st.error(f"Erreur lors de la sauvegarde du match : {e}")
            raise
