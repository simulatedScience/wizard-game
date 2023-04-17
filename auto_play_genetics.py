"""
this module implements methods to automatically let AIs
  play a specified number of games to determine which
  one is the best. Contrary to auto_play_games.py,
  this module works on given instances of AIs rather than
  creating the instances itself. This has the limitation of
  not being able to combine different AIs into one player,
  but it allows for differently parametrized instances of the
  same AI to be compared.

last edited: 11.04.2023
author: Sebastian Jost
"""
import tkinter as tk
import multiprocessing as mp

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

from program_files.game_state import Game_State
from program_files.wizard_ais.ai_base_class import Wizard_Base_Ai
from program_files.helper_functions import get_hands


class Genetic_Auto_Play():
  def __init__(self,
               n_players: int,
               ai_instances: list[Wizard_Base_Ai],
               max_rounds: int = 20,
               confidence_level: float = 0.95,
               limit_choices: bool = False, # not implemented
               ):
    """
    initialize auto-play setup

    inputs:
    -------
        n_players (int): number of players in the game
        limit_choices (bool): whether or not to allow the number of bids can equal the number of tricks (not implemented)
        max_rounds (int): number of rounds to be played
        ai_instances (list[Wizard_Base_Ai]): list of AI instances to be used in the games
        confidence_level (float): confidence level for player scores (score = lower bound of confidence interval)
    """
    self.n_players: int = n_players
    self.limit_choices: bool = limit_choices
    self.n_rounds: int = min(max_rounds, 60 // self.n_players) + 1
    self.ai_instances: list[Wizard_Base_Ai] = ai_instances
    self.confidence_level: float = confidence_level / 2 # two-sided confidence interval

    self.games_played = 0


  def auto_play_single_threaded(self, n_games: int) -> np.ndarray:
    """
    automatically play `n_games` with the set AIs and record the results in self.average_scores and self.win_ratios

    This method uses only one thread and runs all games one after the other.

    Args:
        n_games (int): number of games to be played

    returns:
        (np.ndarray): scores for each player as lower bound of confidence interval
    """
    scores: np.ndarray = np.zeros(self.n_games, self.n_players)
    games_played: int = 0

    random_order = np.arange(self.n_players)

    for n in range(n_games):
      np.random.shuffle(random_order)
      ai_instances = [self.ai_instances[i] for i in random_order]
      player_scores: np.ndarray = self.play_game(ai_instances)
      scores[n, :] = player_scores
    # calculate average scores and standard deviations for each player
    avg_scores: np.ndarray = np.cumsum(scores, axis=0) / n_games
    standard_deviations: np.ndarray = np.std(scores, axis=0)
    # calculate confidence intervals
    z_score: float = stats.norm.ppf(1 - (1 - self.confidence_level) / 2)
    lower_confidence_bound: np.ndarray = avg_scores - standard_deviations / np.sqrt(n_games) * z_score
    return lower_confidence_bound


  def play_record_game(self, *_) -> np.ndarray:
    """
    play a single game and return the final scores of the players

    returns:
    --------
        (np.ndarray): final scores of the players
    """
    random_order: np.ndarray = np.arange(self.n_players)
    np.random.shuffle(random_order)
    ai_instances: list[Wizard_Base_Ai] = [self.ai_instances[i] for i in random_order]
    player_scores: np.ndarray = self.play_game(ai_instances)
    player_scores[random_order] = player_scores # record results in proper order
    return player_scores


  def auto_play_multi_threaded(self, 
      n_games: int, 
      process_pool: mp.Pool,
      ) -> np.ndarray:
    """
    automatically play `n_games` with the set AIs and record the results in self.average_scores and self.win_ratios

    This method uses only one thread and runs all games one after the other.

    Args:
        n_games (int): number of games to be played
        reset_stats (bool): whether to start counting at 0 or continue counting old scores

    returns:
        (np.ndarray): average scores for each player
    """
    # play games in parallel
    result_list: list[np.ndarray] = process_pool.map(self.play_record_game, range(n_games))
    # record results
    scores: np.ndarray = np.array(result_list)
    # calculate average scores and standard deviations for each player
    avg_scores: np.ndarray = np.cumsum(scores, axis=0) / n_games
    standard_deviations: np.ndarray = np.std(scores, axis=0)
    # calculate confidence intervals
    z_score: float = stats.norm.ppf(1 - (1 - self.confidence_level) / 2)
    lower_confidence_bound: np.ndarray = avg_scores - standard_deviations / np.sqrt(n_games) * z_score
    return lower_confidence_bound


  def play_game(self, ai_instances: list[Wizard_Base_Ai]):
    """
    play one game with the rules set in `self`
    """
    game = Game_State(n_players=self.n_players, verbosity=0)
    for round_nbr in range(1, self.n_rounds):
      self.play_round(round_nbr, game, self.limit_choices, ai_instances)
    return game.players_total_points


  def play_round(self, round_nbr: int, game: Game_State, limit_choices: bool, ai_instances: list[Wizard_Base_Ai]):
    """
    play the given round with `self.n_players` players.
    """
    # generate hands and determine trump
    # print(f"Starting round {round_nbr}")
    hands, trump_card = get_hands(game.n_players, round_nbr)
    if trump_card is None:
      trump_color = -1
    elif trump_card.value != 14:
      trump_color = trump_card.color
    else:  # trump card is a wizard -> player who "gave cards" determines trump
      trump_color = ai_instances[game.round_starting_player].get_trump_color_choice(
          hands=hands,
          active_player=game.round_starting_player,
          game_state=game)  # game.round_starting_player(
      # game.round_starting_player,
      # hands[game.round_starting_player])
    game.start_round(hands, trump_card, trump_color)
    # handle player predictions
    predictions = np.zeros(game.n_players, dtype=np.int8)
    player_index = game.round_starting_player
    for _ in range(self.n_players):
      ai_bid = ai_instances[game.round_starting_player].get_prediction(
          player_index=player_index,
          game_state=game)
      predictions[player_index] = ai_bid
      player_index = (player_index + 1) % game.n_players
    game.set_predictions(predictions)
    # play tricks of the round
    while game.tricks_to_be_played > 0:
      self.play_trick(game, ai_instances)


  def play_trick(self, game: Game_State, ai_instances: list[Wizard_Base_Ai]):
    """
    play one trick and advance the game object accordingly
    """
    game.start_trick()
    for _ in range(game.n_players):
      action = ai_instances[game.trick_active_player].get_trick_action(
          game_state=game)
      game.perform_action(action)

  def get_player_labels(self):
    """
    generate labels for each player including their name and all AI types used

    Returns:
        list: list of multiline strings containing player information
    """
    player_labels = [""]*6
    for i in range(self.n_players):
      player_label = f"Player {i+1}\n"
      player_label += f"trump: {self.ai_instances[i].color_number_weight}"
      player_label += f", {self.ai_instances[i].color_sum_weight}\n"
      player_label += f"bids:  {self.ai_instances[i].min_value_for_win}"
      player_label += f", {self.ai_instances[i].min_trump_value_for_win}"
      player_label += f", {self.ai_instances[i].round_factor}"
      player_label += f", {self.ai_instances[i].jester_factor}"
      player_label += f", {self.ai_instances[i].prediction_factor}\n"
      player_label += f"trick: {self.ai_instances[i].trump_value_increase}"
      player_label += f", {self.ai_instances[i].wizard_value}"
      player_label += f", {self.ai_instances[i].n_cards_factor}"
      player_label += f", {self.ai_instances[i].remaining_cards_factor}"
      player_labels[i] = player_label
    return player_labels

  def plot_results(self, tkinter_embedded: tk.Frame = None, highlight_final_value=True):
    """
    plot average scores and win ratios currently saved

    inputs:
    -------
      tkinter_embedded (tkinter.Frame): a tkinter frame where the plot is to be shown. If none is given, the plot is shown in a seperate window created by matplotlib.
    """
    player_labels = self.get_player_labels()
    colors = ["#22dd22", "#00aaaa", "#5588ff", "#bb00bb", "#dd2222", "#ff8800"]
    if tkinter_embedded is None:
      fig, axes = plt.subplots(2, sharex=True)
      ax1, ax2 = axes
      for i in range(self.n_players):
        ax1.plot(self.win_ratios[:, i], label=player_labels[i], color=colors[i], alpha=0.5)
        ax1.hlines(
            (self.win_ratios[-1, i],),
            xmin=0,
            xmax=self.games_played,
            linestyle="--",
            color=colors[i])
            # label=self.win_ratios[-1,i])
        ax2.plot(self.scores[:, i], label=player_labels[i], color=colors[i], alpha=0.5)
        ax2.hlines(
            (self.scores[-1, i],),
            xmin=0,
            xmax=self.games_played,
            linestyle="--",
            color=colors[i])
            # label=self.average_scores[-1,i])
      ax1.set_ylabel("win ratio")
      ax2.set_xlabel("game number")
      ax2.set_ylabel("average score")
      ax1.grid(color="#dddddd")
      ax2.grid(color="#dddddd")
      ax2.legend(loc="center left", bbox_to_anchor=(1.02, 1.02))
      # ax2.legend(loc="center right")
      plt.show()
