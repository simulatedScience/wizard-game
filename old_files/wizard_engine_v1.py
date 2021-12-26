from typing import Tuple, List
import numpy as np
from wizard_card import Wizard_Card
from scoring_functions import score_round, score_trick
from colored_text import colored_text as colored


class WizardGame():
    def __init__(self, n_players: int, limit_choices: bool=True):
        """
        initialize a Wizard game.

        inputs:
        -------
            n_players (int) in [3,4,5,6] - number of players
            limit_choices (bool) - if True, the number of predicted points can't equal the number of rounds.
        """
        self.n_players = n_players

    def play_game(self, n_players: int, limit_choices: bool=True):
        # , extra_cards=False):
        """
        start a game with `n_players` players.

        inputs:
        -------
            n_players (int) in [3,4,5,6] - number of players
            limit_choices (bool) - if True, the number of predicted points can't equal the number of rounds.
        """
        # extra_cards (bool) - whether or not to add 6 special extra cards:
        #     - fairy: always looses, except when a dragon is played. Then it wins.
        #     - dragon: always wins, except when a fairy is played. Then it loses.
        #     - bomb: noone wins this round
        #     - werewolf: exchange this card with trump and choose the new trump.
        #     - cloud: the player who wins a round, where the cloud is played,
        #         must increase or decrease their predicted number of points by one.
        #         Whoever plays this card can choose it's color.
        #     - juggler: at the end of a round, where the juggler is played,
        #         all players pass one card to their neighbouring player.
        #         Whoever plays this card can choose it's color.

        # initialize total player scores as array of 0s
        total_points = np.zeros(n_players, dtype=np.int16)
        point_history = np.array([])
        # determine random starting player
        start_player = np.random.randint(n_players)
        for round_nbr in range(1, 60//n_players):
            # play a round, calculate scores and save them for each player
            points = self.play_round(
                round_nbr, start_player, current_points=total_points)
            # save points of that round in history
            point_history = np.vstack([point_history, points])
            # add points to total scores
            total_points += points
            # increment starting player by one
            start_player = (start_player+1) % n_players

        self.print_game_results()


    def play_round(self, round_nbr: int, start_player: int, current_points):
        """
        play the given round with `self.n_players` players.
        """
        hands, trump = get_hands(self.n_players, round_nbr)
        #
        if trump % 15 == 14:
            self.color_inputs[start_player](hands[start_player], trump)
        # get predictions
        predictions = self.get_predictions(start_player, round_nbr, trump)
        # playing of the round
        won_tricks = np.zeros(self.n_players, dtype=np.int16)
        for _ in range(round_nbr):
            trick_winner: int = self.play_trick(hands, start_player, won_tricks,
                            round_nbr, trump, predictions, current_points)
            won_tricks[trick_winner] += 1

    def play_trick(self,
            hands: List[Wizard_Card],
            start_player: int,
            won_tricks: np.typing.NDArray[np.int16],
            round_nbr: int,
            trump: int,
            predictions: np.typing.NDArray[np.int16],
            current_points: np.typing.NDArray[np.int16]) -> int:
        """
        play one trick
        """
        game_info = {"won_tricks": won_tricks,  # number of points won in this round for each player
                     "round_nbr": round_nbr,    # current round number
                     "trump": trump,            # trump in the current round
                     # predictions for the current round for each player
                     "predictions": predictions,
                     "current_points": current_points}   # total number of points for each player
        # NOT DONE
        serving_color: int = -1
        played_cards: List[int] = [-1]*self.n_players
        player: int = start_player
        for i in range(self.n_players):
            player = (player+1) % self.n_players
        # for round_input, hand, player_wins, prediction in zip(self.round_inputs, hands, won_tricks, predictions):
            hand = hands[player]
            action = self.get_round_input(player, hand, serving_color, game_info)
            # get action until it is a valid one.
            while action_invalid(action, hand, serving_color):
                action = self.get_round_input(hand, serving_color, game_info)
            hand.pop(action)
            played_cards[i] = action
        return score_trick(played_cards, trump)


    def get_round_input(
            player: int,
            hand: list,
            serving_color: int,
            game_info: dict):
        


    def print_game_results(self, gained_points_history, total_scores):
        """
        print history and results of a wizard game.

        inputs:
        -------
            gained_points_history (np.ndarray): 2d array of shape `n x 60//n` detailing how many points everyone had at every round.
            total_scores (np.ndarray): array of length `self.n_players` containing the final scores of each player.
        """
        intermediate_results = np.cumsum(gained_points_history, axis=1)
        print("final results:")
        # print table headline
        table_headline = "|"
        for i in range(1, self.n_players+1):
            table_headline += f"  P{i}  |"
        print(table_headline)

        table_seperator = "|" + "------|"*self.n_players
        print(table_seperator)
        # print table body containing intermediate results for each round
        # if a player lost points in a round, that score is marked red.
        for signs, values in zip(gained_points_history, intermediate_results):
            table_line = "|"
            for sign, value in zip(signs, values):
                str_value = f" {value:4} |"
                if sign > 0:
                    table_line += str_value
                else:
                    table_line += colored(str_value, "#ff3333")
            print(table_line)
        print(table_seperator)
        # print final results
        result_line = "|"
        for player_score in total_scores:
            table_headline += f" {player_score:4} |"
        # determine and print winner
        print(f"winning player is:    P{np.argmax(total_scores)+1}")





def action_invalid(action, hand, serving_color):
    """
    check whether or not a given action is valid.
    """
    # check if the player had the played card
    if not action in hand:
        return False
    # check whether card is jester or wizard
    if action.value in [0, 14]:
        return True
    # check whether the color is serving color
    if action.color != serving_color:
        for card in hand:
            if card.color == serving_color:  # player had to serve
                return False
    return True
