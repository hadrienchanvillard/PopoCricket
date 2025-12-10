import pandas as pd
from importlib import invalidate_caches
from utils import (get_client, get_player_id, get_player_name, calcul_delta_elo, get_player_elo, get_player_rank,
                   get_delta_elo)

url_simple = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/simple.png"
url_double = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/double.png"
url_triple = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/triple.png"
url_blank  = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/blank.png"

num_darts_per_round = 3
num_rounds = 20
targets = ["20", "19", "18", "17", "16", "15", "25"]
targets_to_show = ["20", "19", "18", "17", "16", "15", "B"]

def get_icon(n):
    match n:
        case 3:
            return url_triple
        case 2:
            return url_double
        case 1:
            return url_simple
        case _:
            return url_blank


def get_state_from_db(match_id):
    client = get_client()
    response_match_state = (client.table("match_state")
                           .select("player_id", "target", "score")
                           .eq("match_id", match_id)
                           .execute())

    player_ids = list({item["player_id"] for item in response_match_state.data})
    player_list = [get_player_name(int(player_id)) for player_id in player_ids]

    state = pd.DataFrame(
            [
                {name: 0 for name in player_list} for _ in range(7)
            ],
            index = targets
        )

    for data in response_match_state.data:
        state.loc[data["target"], get_player_name(int(data["player_id"]))] = data["score"]

    return state, player_list


def get_points_from_db(match_id, player_list):
    client = get_client()
    response_player_points = (client.table("match_points")
                           .select("player_id", "points")
                           .eq("match_id", match_id)
                           .execute())

    player_points = pd.DataFrame(
        [
            {name: int(0) for name in player_list}
        ],
        index=["points"]
    )

    for data in response_player_points.data:
        player_points.loc["points", get_player_name(int(data["player_id"]))] = data["points"]

    return player_points


def create_match_in_base():
    client = get_client()
    try:
        response = client.table("matches").insert(
            [{"is_finished": False}], count="None"
        ).execute()
        return response.data[0]['id']
    except Exception as e:
        print(e)


class CricketGame:

    def __init__(self, player_list=None, match_id=None):

        if player_list:

            self.id_match = create_match_in_base()
            self.player_list = player_list
            self.multi = 1
            self.total_dart_number = len(player_list) * num_darts_per_round * num_rounds
            self.actual_dart = 1

            self.actual_state = pd.DataFrame(
                [
                    {name: 0 for name in player_list} for _ in range(7)
                ],
                index = targets
            )
            self.player_points = pd.DataFrame(
                [
                    {name: int(0) for name in player_list}
                ],
                index = ["points"]
            )

            self.state_history = {}
            self.points_history = {}

            self.match_ended = False

        elif match_id:

            self.id_match = match_id
            self.actual_state, self.player_list = get_state_from_db(match_id)
            self.player_points = get_points_from_db(match_id, self.player_list)

        else:
            pass

    def print_state(self):
        print(self.actual_state)
        print(self.player_points)

    def get_actual_player(self):
        len_players = len(self.player_list)
        player_number = ((self.actual_dart - 1) // num_darts_per_round) % len_players
        return self.player_list[player_number]

    def get_tour_number(self):
        if self.match_ended:
            return num_rounds
        return (self.actual_dart - 1)//(len(self.player_list) * num_darts_per_round) + 1

    def get_num_remaining_darts(self):
        if self.match_ended:
            return 0
        return 3-((self.actual_dart-1) % 3)

    def get_cell(self, player, target):
        return self.actual_state.loc[target, player]

    def get_points(self, player):
        return int(self.player_points.loc["points", player])

    def get_ranking(self):
        """
        return ex: {"1": ["Alice"], "2": ["Bob", "Tom"]}
        """
        sorted_pairs = self.player_points.loc["points"].sort_values()
        classement = {}
        rang = 1
        last_value = None

        for player, value in sorted_pairs.items():
            if value != last_value:
                classement[str(rang)] = [player]
                last_value = value
                rang += 1
            else:
                classement[str(rang - 1)].append(player)

        return classement

    def get_ranking_to_print(self, for_history=False):
        result = ""
        player_ranking = self.get_ranking()
        ranks = ["🥇", "🥈", "🥉"] + [str(i) for i in range(4, len(player_ranking) + 1)]

        new_ranking = {}
        for rank, players in player_ranking.items():
            players_with_delta = []
            for player in players:
                delta = get_delta_elo(self.id_match, player)
                sign_delta = f"{delta:+}"
                color = "green" if delta >= 0 else "red"
                players_with_delta.append(f"{player} {get_player_elo(player) if not for_history else ''}<span style='color:{color}'>({sign_delta})</span>")
            new_ranking[rank] = players_with_delta

        for rank, (_, players) in zip(ranks, new_ranking.items()):
            result += f"{rank}: {', '.join(players)}  \n"

        return result

    def set_cell(self, player, target, value):
        self.actual_state.loc[target, player] = value

    def set_multi(self, m):
        self.multi = m

    def add_points_to_player(self, player, points):
        self.player_points.loc["points", player] += int(points)

    def return_to_last_state(self):
        prev_round_key = str(self.actual_dart - 1)
        if prev_round_key in self.state_history:
            self.actual_state = self.state_history[prev_round_key]
            self.player_points = self.points_history[prev_round_key]
            self.actual_dart -= 1
            self.match_ended = False

    def is_player_winning(self, player):
        if self.actual_state.loc[:, player].tolist() == [3] * 7:
            player_points = self.player_points.loc["points", player]
            for other_player in self.player_list:
                if other_player != player and self.player_points.loc["points", other_player] <= player_points:
                    return False
            return True
        return False

    def check_end_match(self):
        if self.actual_dart > self.total_dart_number:
            return True

        for player in self.player_list:
            if self.is_player_winning(player):
                return True

        return False

    def throw(self, target):
        if not self.match_ended:
            self.state_history[str(self.actual_dart)]  = self.actual_state.copy()
            self.points_history[str(self.actual_dart)] = self.player_points.copy()

            actual_player = self.get_actual_player()

            if target != "0":
                # add points to other players
                if self.get_cell(actual_player, target) + self.multi > 3:
                    added_points = int((self.get_cell(actual_player, target) + self.multi - 3) * int(target))
                    for other_player in self.player_list:
                        if other_player != actual_player and  self.get_cell(other_player, target) < 3:
                            self.add_points_to_player(other_player, added_points)

                # update actual player score
                self.set_cell(actual_player, target, min(self.get_cell(actual_player, target) + self.multi, 3))

            self.multi=1
            self.actual_dart += 1
            self.match_ended = self.check_end_match()

    def get_df_to_print(self):
        df_w_icon = pd.DataFrame(
            {
                player: [get_icon(self.actual_state.loc[target, player]) for target in targets]
                for player in self.player_list
            },
            index=targets_to_show,
            dtype=object
        )

        return df_w_icon, self.player_points

    def state_to_base(self):
        client = get_client()
        for player in self.player_list:
            player_id = get_player_id(player)
            points = self.player_points.loc["points", player].item()

            try:
                client.table("match_points").insert(
                    [{
                        "match_id": self.id_match,
                        "player_id": player_id,
                        "points": points,
                    }], count="None"
                ).execute()
            except Exception as e:
                print(e)

            for target in targets:
                score = self.actual_state.loc[target, player].item()

                try:
                    client.table("match_state").insert(
                        [{
                            "match_id": self.id_match,
                            "player_id": player_id,
                            "target": target,
                            "score": score
                        }], count="None"
                    ).execute()
                except Exception as e:
                    print(e)
        try:
            client.table("matches").update(
                {"is_finished": True}
            ).eq("id", self.id_match).execute()
        except Exception as e:
            print(e)

        players_ranking = self.get_ranking()
        deltas_elo = calcul_delta_elo(players_ranking, self.player_list)

        for player in self.player_list:
            old_elo = get_player_elo(player)
            delta_elo = deltas_elo[player]
            try:
                client.table("match_ranking").insert(
                    [{
                        "match_id": self.id_match,
                        "player_id": get_player_id(player),
                        "rank": get_player_rank(players_ranking, player),
                        "old_elo": old_elo,
                        "new_elo": old_elo + delta_elo,
                        "delta_elo": delta_elo
                    }], count="None"
                ).execute()
            except Exception as e:
                print(e)

            try:
                (client.
                 table("players")
                 .update({"player_elo": old_elo + delta_elo})
                 .eq("id", get_player_id(player))
                 .execute())
            except Exception as e:
                print(e)

            invalidate_caches()

# g=CricketGame(["paul", "max", "jean"])
# g.print_state()
# for _ in range(4):
#     g.throw("20")
# g.print_state()
# print(g.actual_state.loc[:, "paul"].tolist() == [3]+[0]*7)
# g.return_to_last_state()
# g.print_state()

