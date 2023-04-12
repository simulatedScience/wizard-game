"""
this module implements methods to automatically let AIs
    play a specified number of games to determine which
    one is the best.

last edited: 26.05.2022
author: Sebastian Jost
version 0.2
"""
import tkinter as tk
import multiprocessing as mp

import numpy as np
import matplotlib.pyplot as plt

from program_files.game_state import Game_State
from program_files.helper_functions import get_hands
from program_files.wizard_ais.wizard_ai_classes import ai_trump_chooser_methods, ai_bids_chooser_methods, ai_trick_play_methods


class Wizard_Auto_Play():
  def __init__(self,
               n_players,
               ai_player_types: list,
               limit_choices: bool = False,
               max_rounds: int = 20,
               shuffle_players: bool = False):
    """
    initialize auto-play setup

    inputs:
    -------
      n_players (int): number of players in the game
      limit_choices (bool): whether or not to allow the number of bids can equal the number of tricks
        max_rounds (int): number of rounds to be played
        ai_player_choices (list) of (dict): settings for player names  to use AI to calculate actions during the game.
        shuffle_players (bool): whether to randomize the order of players between games for more general results.
    """
    self.n_players = n_players
    self.limit_choices = limit_choices
    self.n_rounds = min(max_rounds, 60 // self.n_players) + 1
    self.ai_player_types = ai_player_types
    self.shuffle_players = shuffle_players

    self.games_played = 0
    self.set_history_variables(n_players, 0)


  def set_history_variables(self, n_players, n_games):
    self.average_scores: np.ndarray = np.zeros((n_games, n_players))
    self._score_sums: np.ndarray = np.zeros(n_players)
    self.relative_scores: np.ndarray = np.zeros(n_players)
    self._win_counts: np.ndarray = np.zeros(n_players)
    self.win_ratios: np.ndarray = np.zeros((n_games, n_players))


  def auto_play_single_threaded(self,
      n_games: int, 
      reset_stats: bool = True):
    """
    automatically play `n_games` with the set AIs and record the results in self.average_scores, self.relative_scores and self.win_ratios

    This method uses only one thread and runs all games one after the other.

    Args:
        n_games (int): number of games to be played
        reset_stats (bool): whether to start counting at 0 or continue counting old scores

    returns:
        (np.ndarray): average scores for each player
        (np.ndarray): win ratio for each player
    """
    if reset_stats:  # reset statistics
      self.set_history_variables(self.n_players, n_games)
      n_games_start = 0
      n_games_end = n_games
    else:  # continue counting with old scores
      n_games_start = self.average_scores.shape[0]
      n_games_end = n_games_start + n_games
      self.average_scores = np.vstack(
          [self.win_ratios, np.zeros(n_games, self.n_players)])
      self.win_ratios = np.vstack(
          [self.win_ratios, np.zeros(n_games, self.n_players)])

    if self.shuffle_players:
      self.random_order = np.arange(self.n_players)

    for n in range(n_games_start, n_games_end):
      if self.shuffle_players:
        np.random.shuffle(self.random_order)
        ai_player_types = [self.ai_player_types[i] for i in self.random_order]
      else:
        ai_player_types = self.ai_player_types
      player_scores = self.play_game(ai_player_types)
      # update history variables
      self.games_played += 1
      if self.shuffle_players:
        self._score_sums[self.random_order] += player_scores
        self.average_scores[n, :] = self._score_sums / self.games_played
        self._win_counts[self.random_order] += player_scores == np.max(player_scores)
        self.win_ratios[n, :] = self._win_counts / np.sum(self._win_counts)
      else:
        self._score_sums += player_scores
        self.average_scores[n, :] = self._score_sums / self.games_played
        self._win_counts += player_scores == np.max(player_scores)
        self.win_ratios[n, :] = self._win_counts / np.sum(self._win_counts)

    return self.average_scores, self.win_ratios


  def play_record_game(self, n: int) -> np.ndarray:
    if self.shuffle_players:
      np.random.shuffle(self.random_order)
      ai_player_types = [self.ai_player_types[i] for i in self.random_order]
    else:
      ai_player_types = self.ai_player_types
    player_scores = self.play_game(ai_player_types)
    player_scores[self.random_order] = player_scores # record results in proper order
    return player_scores


  def auto_play_multi_threaded(self, 
      n_games: int, 
      reset_stats: bool = True):
    """
    automatically play `n_games` with the set AIs and record the results in self.average_scores, self.relative_scores and self.win_ratios

    This method uses only one thread and runs all games one after the other.

    Args:
        n_games (int): number of games to be played
        reset_stats (bool): whether to start counting at 0 or continue counting old scores

    returns:
        (np.ndarray): average scores for each player
        (np.ndarray): win ratio for each player
    """
    if reset_stats:  # reset statistics
      self.set_history_variables(self.n_players, n_games)
      n_games_start = 0
      n_games_end = n_games
    else:  # continue counting with old scores
      n_games_start = self.average_scores.shape[0]
      n_games_end = n_games_start + n_games
      self.average_scores = np.vstack(
          [self.win_ratios, np.zeros(n_games, self.n_players)])
      self.win_ratios = np.vstack(
          [self.win_ratios, np.zeros(n_games, self.n_players)])

    if self.shuffle_players:
      self.random_order = np.arange(self.n_players)

    process_pool: mp.Pool = mp.Pool(mp.cpu_count() * 2)
    new_results = process_pool.map(self.play_record_game, range(n_games_start, n_games_end))
    process_pool.close()
    process_pool.join()

    # update history variables
    for i, player_scores in enumerate(new_results):
      n = i + n_games_start
      self.games_played += 1
      if self.shuffle_players:
        self._score_sums += player_scores
        self.average_scores[n, :] = self._score_sums / self.games_played
        self._win_counts += player_scores == np.max(player_scores)
        self.win_ratios[n, :] = self._win_counts / np.sum(self._win_counts)
      else:
        self._score_sums += player_scores
        self.average_scores[n, :] = self._score_sums / self.games_played
        self._win_counts += player_scores == np.max(player_scores)
        self.win_ratios[n, :] = self._win_counts / np.sum(self._win_counts)
      

    return self.average_scores, self.win_ratios


  def play_game(self, ai_player_types: list):
    """
    play one game with the rules set in `self`
    """
    game = Game_State(n_players=self.n_players, verbosity=0)
    for round_nbr in range(1, self.n_rounds):
      self.play_round(round_nbr, game, self.limit_choices, ai_player_types)
    return game.players_total_points


  def play_round(self, round_nbr: int, game: Game_State, limit_choices: bool, ai_player_types: list):
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
      player_mode = ai_player_types[game.round_starting_player]["trump_choice_var"]
      trump_color = ai_trump_chooser_methods[player_mode](
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
      player_mode = ai_player_types[game.trick_active_player]["bids_choice_var"]
      ai_bid = ai_bids_chooser_methods[player_mode](
          player_index=player_index,
          game_state=game)
      predictions[player_index] = ai_bid
      player_index = (player_index + 1) % game.n_players
    game.set_predictions(predictions)
    # play tricks of the round
    while game.tricks_to_be_played > 0:
      self.play_trick(game, ai_player_types)


  def play_trick(self, game, ai_player_types):
    """
    play one trick and advance the game object accordingly
    """
    game.start_trick()
    for _ in range(game.n_players):
      player_mode = ai_player_types[game.trick_active_player]["get_trick_action"]
      action = ai_trick_play_methods[player_mode](
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
      player_label += f"trump: {self.ai_player_types[i]['trump_choice_var']}\n"
      player_label += f"bids:  {self.ai_player_types[i]['bids_choice_var']}\n"
      player_label += f"trick: {self.ai_player_types[i]['get_trick_action']}"
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
        ax2.plot(self.average_scores[:, i], label=player_labels[i], color=colors[i], alpha=0.5)
        ax2.hlines(
            (self.average_scores[-1, i],),
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
      # adjust borders of figure
      fig.subplots_adjust(left=0.05, right=0.85, top=0.95, bottom=0.1)
      plt.show()
