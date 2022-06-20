"""
This module implements the engine of the wizard game in a class `Wizard_Game`.
This class uses 

last edited: 25.05.2022
author: Sebastian Jost
version 0.2
"""
import numpy as np

from program_files.colored_text import colored_text as colored
from program_files.wizard_game_state import Wizard_Game_State
from program_files.wizard_functions import get_hands
import program_files.wizard_inputs as player_inputs


class Wizard_Game():
    def __init__(self, n_players: int):
        """
        initialize a Wizard game.

        inputs:
        -------
            n_players (int) in [3,4,5,6] - number of players
            limit_choices (bool) - if True, the number of predicted points can't equal the number of rounds.
        """
        self.n_players = n_players


    def play_game(self, limit_choices: bool = True, max_rounds: int = 20) -> None:
        # , extra_cards=False):
        """
        start a game with `n_players` players.

        inputs:
        -------
            n_players (int) in [3,4,5,6] - number of players
            limit_choices (bool) - if True, the number of predicted points can't equal the number of rounds.
            max_rounds (int) - maximum number of rounds to be played, starting at round 1

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
        """
        # initialize object to save the game state
        game = Wizard_Game_State(n_players=self.n_players, verbosity=2)
        n_rounds = min(max_rounds, 60 // self.n_players) + 1
        for round_nbr in range(1, n_rounds):
            self.play_round(round_nbr, game, limit_choices)
            print("\n", "#" * 60, "\n", sep="")
        self.print_game_results(game)


    def play_round(self, round_nbr: int, game: Wizard_Game_State, limit_choices: bool):
        """
        play the given round with `self.n_players` players.
        """
        # generate hands and determine trump
        print(f"Starting round {round_nbr}")
        hands, trump_card = get_hands(game.n_players, round_nbr)
        if trump_card is None:
            trump_color = -1
        elif trump_card.value != 14:
            trump_color = trump_card.color
        else:  # trump card is a wizard -> player who "gave cards" determines trump
            trump_color = player_inputs.trump_color_input(
                game.round_starting_player,
                hands[game.round_starting_player])
        game.start_round(hands, trump_card, trump_color)
        # handle player predictions
        predictions = player_inputs.get_predictions(game, round_nbr, limit_choices)
        game.set_predictions(predictions)
        # play tricks of the round
        while game.tricks_to_be_played > 0:
            self.play_trick(game)


    def play_trick(self,
                   game: Wizard_Game_State,
                   ) -> int:
        """
        play one trick
        """
        game.start_trick()
        for _ in range(game.n_players):
            action = player_inputs.get_action_input(game)
            game.perform_action(action)


    def print_game_results(self, game: Wizard_Game_State):
        """
        print history and results of a wizard game.

        inputs:
        -------
            gained_points_history (np.ndarray): 2d array of shape `n x 60//n` detailing how many points everyone had at every round.
            total_scores (np.ndarray): array of length `self.n_players` containing the final scores of each player.
        """
        gained_points_history = game.players_gained_points_history
        total_scores = game.players_total_points
        intermediate_results = np.cumsum(gained_points_history, axis=0, dtype=np.int16)
        print("final results:")
        # print table headline
        table_headline = "|"
        for i in range(1, self.n_players + 1):
            table_headline += f"   P{i}  |"
        print(table_headline)

        table_seperator = "|" + "-------|" * self.n_players
        print(table_seperator)
        # print table body containing intermediate results for each round
        # if a player lost points in a round, that score is marked red.
        for signs, values in zip(gained_points_history, intermediate_results):
            table_line = "|"
            for sign, value in zip(signs, values):
                str_value = f" {value:5} "
                if sign > 0:
                    table_line += str_value
                else:
                    table_line += colored(str_value, "#ff3333")
                table_line += "|"
            print(table_line)
        print(table_seperator)
        # print final results
        result_line = "|"
        for player_score in total_scores:
            result_line += f" {player_score:5} |"
        print(result_line)
        # determine and print winner
        print(f"winning player is:    P{np.argmax(total_scores)+1}")



if __name__ == "__main__":
    game = Wizard_Game(n_players=3)
    game.play_game(limit_choices=True)
