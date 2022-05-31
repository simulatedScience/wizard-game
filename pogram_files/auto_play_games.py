"""
this module implements methods to automatically let AIs
    play a specified number of games to determine which
    one is the best.

last edited: 26.05.2022
author: Sebastian Jost
version 0.2
"""
import numpy as np

from pogram_files.wizard_game_state import Wizard_Game_State
from pogram_files.wizard_functions import get_hands
from pogram_files.wizard_ais.wizard_ai_classes import ai_trump_chooser_methods, ai_bids_chooser_methods, ai_trick_play_methods


class Wizard_Auto_Play():
  def __init__(self,
               n_players,
               limit_choices: bool,
               max_rounds: int,
               ai_player_types: list):
    """
    initialize auto-play setup

    inputs:
    -------
      n_players (int): number of players in the game
      limit_choices (bool): whether or not to allow the number of bids can equal the number of tricks
        max_rounds (int): number of rounds to be played
        ai_player_choices (list) of (dict): settings for player names  to use AI to calculate actions during the game.
    """
    self.n_players = n_players
    self.limit_choices = limit_choices
    self.n_rounds = min(max_rounds, 60 // self.n_players) + 1
    self.ai_player_types = ai_player_types

    self.games_played = 0
    self.set_history_variables(n_players, 0)


  def set_history_variables(self, n_players, n_games):
    self.average_scores: np.ndarray = np.zeros((n_games, n_players))
    self._score_sums: np.ndarray = np.zeros(n_players)
    self.relative_scores: np.ndarray = np.zeros(n_players)
    self.win_counts: np.ndarray = np.zeros(n_players)
    self.win_ratios: np.ndarray = np.zeros((n_games, n_players))


  def auto_play_single_threaded(self, n_games: int, reset_stats: bool = True):
    """
    automatically play `n_games` with the set AIs and record the results in self.average_scores, self.relative_scores and self.win_ratios

    This method uses only one thread and runs all games one after the other.

    Args:
        n_games (int): number of games to be played
        reset_stats (bool): whether to start counting at 0 or continue counting old scores

    returns:
        (np.ndarray): average scores for eac player
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

    for n in range(n_games_start, n_games_end):
      player_scores = self.play_game()
      # update history variables
      self.games_played += 1
      self._score_sums += player_scores
      self.average_scores[n, :] = self._score_sums / self.games_played
      self.win_counts += np.where(player_scores == np.max(player_scores))
      self.win_ratios[n, :] = self.win_counts / np.sum(self.win_counts)

    return self.average_scores, self.win_ratios


  def play_game(self):
    """
    play one game with the rules set in `self`
    """
    game = Wizard_Game_State(n_players=self.n_players, verbosity=2)
    for round_nbr in range(1, self.n_rounds):
      self.play_round(round_nbr, game, self.limit_choices)

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
      player_mode = self.ai_player_types[game.round_starting_player]["trump_choice_var"]
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
      player_mode = self.ai_player_types[game.player_index]["bids_choice_var"]
      ai_bid = ai_bids_chooser_methods[player_mode](
          player_index=player_index,
          game_state=game)
      predictions[player_index] = ai_bid
      player_index = (player_index + 1) % game.n_players
    game.set_predictions(predictions)
    # play tricks of the round
    while game.tricks_to_be_played > 0:
      self.play_trick(game)

  def play_trick(self, game):
    """play one trick and advance the game object accordingly"""
