"""
this module implements methods to automatically let AIs
    play a specified number of games to determine which
    one is the best.

last edited: 26.05.2022
author: Sebastian Jost
version 0.2
"""
import numpy as np


class Wizard_Auto_Play():
  def __init__(self,
               n_players,
               limit_choices: bool,
               max_rounds: int,
               ai_player_choices: list):
    """
    initialize auto-play setup

    inputs:
    -------
      n_players (int): number of players in the game
      limit_choices (bool): whether or not to allow the number of bids can equal the number of tricks
        max_rounds (int): number of rounds to be played
        ai_player_choices (list) of (dict): settings for player names and whether to use AI to calculate actions during the game.
    """
    self.n_players = n_players
    self.limit_choices = limit_choices
    self.n_rounds = min(max_rounds, 60 // self.n_players) + 1
    self.ai_player_choices = ai_player_choices

    self.games_played = 0
    self.set_history_variables(n_players, 0)


  def set_history_variables(self, n_players, n_games):
    self.average_scores: np.ndarray = np.zeros((n_games, n_players))
    self._score_sums: np.ndarray = np.zeros(n_players)
    self.relative_scores: np.ndarray = np.zeros(n_players)
    self.win_counts: np.ndarray = np.zeros(n_players)
    self.win_ratios: np.ndarray = np.zeros((n_games, n_players))


  def auto_play_single_threaded(self, n_games, reset_stats=True):
    """
    automatically play `n_games` with the set AIs and record the results in self.average_scores, self.relative_scores and self.win_ratios

    This method uses only one thread and runs all games one after the other.

    Args:
        n_games (int): number of games to be played
    """
    if reset_stats:
      self.set_history_variables(self.n_players, n_games)
      n_games_start = 0
      n_games_end = n_games
    else:
      n_games_start = self.average_scores.shape[0]
      n_games_end = n_games_start + n_games
      self.average_scores = np.vstack(
          [self.win_ratios, np.zeros(n_games, self.n_players)])
      self.win_ratios = np.vstack(
          [self.win_ratios, np.zeros(n_games, self.n_players)])

    for n in range(n_games_start, n_games_end):
      player_scores = self.play_game()
      self.games_played += 1
      self._score_sums += player_scores
      self.average_scores[n, :] = self._score_sums / self.games_played
      self.win_counts += np.where(player_scores == np.max(player_scores))
      self.win_ratios[n, :] = self.win_counts / np.sum(self.win_counts)
    return self.average_scores, self.win_ratios


  def play_game(self):
