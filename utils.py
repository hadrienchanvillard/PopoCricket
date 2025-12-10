import streamlit as st
from st_supabase_connection import SupabaseConnection
from typing import List, Dict, Optional


@st.cache_resource
def get_client():
    """Retourne le client Supabase."""
    conn = st.connection("supabase", type=SupabaseConnection)
    return conn.client


def get_player_list() -> List[str]:
    """Retourne la liste des noms de joueurs."""
    client = get_client()
    player_list = client.table("players").select("player_name").execute()
    return [player["player_name"] for player in player_list.data]


def get_leaderbord() -> List[Dict]:
    """Retourne le classement ELO des joueurs."""
    client = get_client()
    return client.table("players").select("player_name", "player_elo").order("player_elo", desc=True).execute().data


@st.cache_data
def get_player_id(player_name: str) -> Optional[int]:
    """Retourne l'ID d'un joueur à partir de son nom."""
    client = get_client()
    result = (
        client
        .table("players")
        .select("id")
        .eq("player_name", player_name)
        .execute()
    )
    return result.data[0]["id"] if result.data else None


def get_player_elo(player_name: str) -> Optional[float]:
    """Retourne l'ELO actuel d'un joueur."""
    client = get_client()
    result = (
        client
        .table("players")
        .select("player_elo")
        .eq("player_name", player_name)
        .execute()
    )
    return float(result.data[0]["player_elo"]) if result.data else None


@st.cache_data
def get_player_name(player_id: int) -> Optional[str]:
    """Retourne le nom d'un joueur à partir de son ID."""
    client = get_client()
    result = (
        client
        .table("players")
        .select("player_name")
        .eq("id", player_id)
        .execute()
    )
    return result.data[0]["player_name"] if result.data else None


@st.cache_data
def get_delta_elo(match_id: int, player: str) -> Optional[float]:
    """Retourne la variation d'ELO d'un joueur pour un match donné."""
    client = get_client()
    result = (
        client
        .table("match_ranking")
        .select("delta_elo")
        .eq("match_id", match_id)
        .eq("player_id", get_player_id(player))
        .execute()
    )
    return result.data[0]["delta_elo"] if result.data else None


def get_player_rank(players_ranking: Dict[str, List[str]], player_name: str) -> Optional[int]:
    """Retourne le rang d'un joueur dans un classement donné."""
    for rank, players in players_ranking.items():
        if player_name in players:
            return int(rank)
    return None


def calcul_delta_elo(players_ranking: Dict[str, List[str]], player_list: List[str]) -> Dict[str, float]:
    """
    Calcule les variations d'ELO pour tous les joueurs selon le système ELO.

    Args:
        players_ranking: Classement des joueurs {rang: [joueurs]}
        player_list: Liste des joueurs du match

    Returns:
        Dictionnaire {joueur: delta_elo}
    """
    result = {}

    player_elo_rank = {}
    for player in player_list:
        player_elo_rank[player] = {
            "elo": get_player_elo(player),
            "rank": get_player_rank(players_ranking, player)
        }

    for player in player_list:
        delta = 0
        for other_player in player_list:
            if other_player != player:
                prob = 1 / (1 + 10 ** ((player_elo_rank[other_player]["elo"] - player_elo_rank[player]["elo"]) / 400))

                if player_elo_rank[player]["rank"] < player_elo_rank[other_player]["rank"]:
                    real = 1
                elif player_elo_rank[player]["rank"] == player_elo_rank[other_player]["rank"]:
                    real = 0.5
                else:
                    real = 0

                delta += real - prob

        delta = round((32 * delta) / (len(player_list) - 1), 2)
        result[player] = delta

    return result