import pandas as pd

url_simple = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/simple.png"
url_double = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/double.png"
url_triple = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/triple.png"
url_blank  = "https://jjdotprdoyufgsvcgnky.supabase.co/storage/v1/object/public/cricket%20icons/blank.png"

num_darts_per_round = 3
num_rounds = 20

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
                {name: int(0) for name in player_list}
            ],
            index = ["points"]
        )

        self.multi = 1

        self.state_history = {}
        self.points_history = {}

        self.total_dart_number = len(player_list) * num_darts_per_round * num_rounds
        self.actual_dart = 1

        self.game_ended = False

    def print_state(self):
        print(self.actual_state)
        print(self.player_points)

    def get_actual_player(self):
        len_players = len(self.player_list)
        player_number = ((self.actual_dart - 1) // num_darts_per_round) % len_players
        return self.player_list[player_number]

    def get_tour_number(self):
        if self.game_ended:
            return num_rounds
        return (self.actual_dart - 1)//(len(self.player_list) * num_darts_per_round) + 1

    def get_num_remaining_darts(self):
        if self.game_ended:
            return 0
        return 3-((self.actual_dart-1) % 3)

    def get_cell(self, player, target):
        return self.actual_state.loc[target, player]

    def get_points(self, player):
        return int(self.player_points.loc["points", player])

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
            self.game_ended = False

    def is_player_winning(self, player):
        if self.actual_state.loc[:, player].tolist() == [3] * 7:
            player_points = self.player_points.loc["points", player]
            for other_player in self.player_list:
                if other_player != player and self.player_points.loc["points", other_player] <= player_points:
                    return False
            return True
        return False

    def check_end_game(self):
        if self.actual_dart > self.total_dart_number:
            return True

        for player in self.player_list:
            if self.is_player_winning(player):
                return True

        return False

    def throw(self, target):
        if not self.game_ended:
            self.state_history[str(self.actual_dart)]  = self.actual_state.copy()
            self.points_history[str(self.actual_dart)] = self.player_points.copy()

            actual_player = self.get_actual_player()

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
            self.game_ended = self.check_end_game()

    def get_df_to_print(self):
        targets = ["20", "19", "18", "17", "16", "15", "25"]

        df_w_icon = pd.DataFrame(
            {
                name: [get_icon(self.actual_state.loc[target, name]) for target in targets]
                for name in self.player_list
            },
            index=targets,
            dtype=object
        )

        return df_w_icon, self.player_points


# g=CricketGame(["paul", "max", "jean"])
# g.print_state()
# for _ in range(4):
#     g.throw("20")
# g.print_state()
# print(g.actual_state.loc[:, "paul"].tolist() == [3]+[0]*7)
# g.return_to_last_state()
# g.print_state()

