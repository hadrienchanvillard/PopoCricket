import pandas as pd

url_simple = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/simple.png"
url_double = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/double.png"
url_triple = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/triple.png"
url_blank  = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/blank.png"


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

class CricketGame:

    def __init__(self, player_list):

        self.player_list = player_list

        self.actual_state = pd.DataFrame(
            [
                {name: 0 for name in player_list} for _ in range(7)
            ],
            index = ["20", "19", "18", "17", "16", "15", "25"]
        )

        self.player_points = pd.DataFrame(
            [
                {name: 0 for name in player_list}
            ],
            index = ["points"]
        )

        self.state_history = {}
        self.points_history = {}

        self.total_round_number = len(player_list) * 20
        self.actual_round = 1


    def print_state(self):
        print(self.actual_state)
        print(self.player_points)

    def get_actual_player(self):
        len_players = len(self.player_list)
        player_number = ((self.actual_round - 1) // len_players) % len_players
        return self.player_list[player_number]

    def get_cell(self, player, target):
        return self.actual_state.loc[target, player]

    def get_points(self, player):
        return self.player_points.loc[player, "points"]

    def set_cell(self, player, target, value):
        self.actual_state.loc[target, player] = value

    def add_points_to_player(self, player, points):
        self.player_points.loc["points", player] += points

    def return_to_last_state(self):
        prev_round_key = str(self.actual_round - 1)
        if prev_round_key in self.state_history:
            self.actual_state = self.state_history[prev_round_key]
            self.player_points = self.points_history[prev_round_key]
            self.actual_round -= 1

    def throw(self, target, multi=1):
        self.state_history[str(self.actual_round)]  = self.actual_state.copy()
        self.points_history[str(self.actual_round)] = self.player_points.copy()

        actual_player = self.get_actual_player()

        # add points to other players
        if self.get_cell(actual_player, target) + multi > 3:
            added_points = int((self.get_cell(actual_player, target) + multi - 3) * target)
            for other_player in self.player_list:
                if other_player != actual_player and  self.get_cell(other_player, target) < 3:
                    self.add_points_to_player(other_player, added_points)

        # update actual player score
        self.set_cell(actual_player, target, min(self.get_cell(actual_player, target) + multi, 3))

        self.actual_round += 1

    def get_df_to_print(self):
        targets = ["20", "19", "18", "17", "16", "15", "25"]

        df = pd.DataFrame(
            {
                name: [get_icon(self.actual_state.loc[target, name]) for target in targets]
                for name in self.player_list
            },
            index=targets,
            dtype=object
        )
        return df, self.player_points


# g=CricketGame(["paul", "max", "jean"])
# g.print_state()
# for _ in range(4):
#     g.throw("20", 2)
# g.print_state()
# g.return_to_last_state()
# g.print_state()

