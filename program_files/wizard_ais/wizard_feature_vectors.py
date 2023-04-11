"""
This module contains functions to create feature vectors as compressed representations of the current game state of a Wizard game.
"""

import torch
import numpy as np

from program_files.game_state import Game_State
from program_files.wizard_card import Wizard_Card
from program_files.helper_functions import check_action_invalid
from program_files.scoring_functions import update_winning_card


def get_trump_choice_features(
      hands: list[list[Wizard_Card]],
      active_player: int,
      game_state: Game_State) -> torch.Tensor:
  """
  create a feature vector for the trump color choice neural network
  This vector includes (shape: (18,)):
    for i in [0, 1, 2, 3]:
    - [0 - 8]: number of cards of color i, 
    - [0 - 13]: average value of cards of color i
    - [0 - 13]: minimum value of cards of color i
    - [0 - 13]: maximum value of cards of color i
    - [0 - 4]: number of wizards in hand
    - [0 - 4]: number of jesters in hand

  inputs:
  -------
      hands  list[list[Wizard_Card]]): list of cards in hand of the active player
      active_player (int): integer representing the active player index
      game_state (Wizard_Game_State): object representing the current state of the game

  returns:
  --------
      torch.Tensor: feature vector
  """
  hand: list[Wizard_Card] = hands[active_player]
  feature_vector: torch.Tensor = torch.zeros(18)
  # color-specific features
  for i in range(4):
    color_cards = [card for card in hand if card.color == i]
    feature_vector[4*i] = len(color_cards)
    if len(color_cards) > 0:
      card_values: list[int] = [card.value for card in color_cards]
      feature_vector[4*i + 1] = sum(card_values) / len(color_cards) # average value
      feature_vector[4*i + 2] = min(card_values) # minimum value
      feature_vector[4*i + 3] = max(card_values) # maximum value
  # number of wizards
  feature_vector[16] = len([card for card in hand if card.value == 14])
  # number of jesters
  feature_vector[17] = len([card for card in hand if card.value == 0])
  return feature_vector


def get_prediction_features(
    player_index: int,
    game_state: Game_State):
  """
  create a feature vector for the bid prediction neural network

  Feature vector includes (shape: (20,)): # TODO: (22,) once Game_State updates bids immediately
    for i in [0, 1, 2, 3]:
    - [0 - 8]: number of cards of color i, 
    - [0 - 13]: average value of cards of color i
    - [0 - 13]: minimum value of cards of color i
    - [0 - 13]: maximum value of cards of color i
    - [0 - 4]: number of wizards in hand
    - [0 - 4]: number of jesters in hand
    - [0 - 6]: number of players left to bid
    - [0 - 4]: number of players who already declared their bid
    # - [-48 - 20]: number of tricks left # not supported by Game_State yet
    # - [0 - 60]: sum of previous player's bids # not supported by Game_State yet
  """
  feature_vector: torch.Tensor = torch.zeros(22)
  # color-specific and wizard/ jester features
  feature_vector[0:18] = get_trump_choice_features(game_state.players_hands, player_index, game_state)
  # number of players left to bid
  feature_vector[18] = game_state.n_players - (player_index - game_state.round_starting_player) % game_state.n_players
  # number of players who already declared their bid
  feature_vector[19] = (player_index - game_state.round_starting_player) % game_state.n_players
  # number of tricks left
  # feature_vector[20] = game_state.round_number - np.sum(game_state.players_predictions)
  # sum of previous player's bids
  # feature_vector[21] = np.sum(game_state.players_predictions)
  return feature_vector

def get_trick_action_features(
    game_state: Game_State) -> torch.Tensor:
  """
  create a feature vector for the trick action neural network

  Feature vector includes (shape: (22, len(valid_actions))):
  - [0 - 4]: number of wizards in hand
  - [0 - 4]: number of jesters in hand
  - [0 - 12]: number of trumps in hand
  - [0, 1] and [0 - 14]: color and value of highest trump card in hand (if any)
  - [0 - 4] and [0 - 14]: color and value of highest non-trump card in hand (if any)
  - [0 - 20]: number of cards in hand that could be played without taking the lead # TODO: exclude trumps
  # features describing the current card
  - [0 - 14]: value of current card
  - [0 - 4]: color of current card
  - [0, 1]: whether current card is a wizard
  - [0, 1]: whether current card is a trump
  - [0, 1]: whether current leading card can be beaten by a lower card of the same color
  - [0 - 13]: number of cards in hand of the same color as current card

  - [0 - 12]: number of cards in hand of the same color as current leading card
  - [0 - 5]: number of players playing after current player in current trick
  - [0 - 5]: number of cards in current trick
  - [0, 1]: whether current leading card is a wizard
  - [0 - 4]: color of current leading card in trick
  - [0 - 14]: value of current leading card in trick

  - [0 - 4]: serving color
  - [-20 - 20]: number of tricks needed to match bid

  inputs:
  -------
      card (Wizard_Card): card to be evaluated
      game_state (Wizard_Game_State): object representing the current state of the game

  returns:
  --------
      torch.Tensor: one feature vector for each valid action
      list[int]: list of indices of valid actions
  """
  hand: list[Wizard_Card] = game_state.players_hands[game_state.trick_active_player]
  valid_indices: list[int] = [i for i, card in enumerate(hand) if not check_action_invalid(card, hand, game_state.serving_color)]
  valid_actions = [hand[i] for i in valid_indices]
  loosing_actions, winning_actions = _get_winning_actions(valid_actions, game_state)

  feature_tensor: torch.Tensor = torch.zeros(22, len(valid_actions))
  ### features describing the player's hand
  # number of wizards
  feature_tensor[0, :] = len([card for card in hand if card.value == 14])
  # number of jesters
  feature_tensor[1, :] = len([card for card in hand if card.value == 0])
  # number of trumps
  trump_cards: list[Wizard_Card] = [card for card in hand if card.color == game_state.trump_color]
  feature_tensor[2, :] = len(trump_cards)
  # highest trump card
  if len(trump_cards) > 0:
    trump_values: list[int] = [card.value for card in trump_cards]
    feature_tensor[3, :] = max(trump_values)
    feature_tensor[4, :] = game_state.trump_color
  # highest non-trump card
  non_trump_cards: list[Wizard_Card] = [card for card in hand if card.color != game_state.trump_color and card.value % 14 != 0]
  if len(non_trump_cards) > 0:
    non_trump_values: list[int] = [card.value for card in non_trump_cards]
    feature_tensor[5, :] = max(non_trump_values)
    feature_tensor[6, :] = max(non_trump_values) % 14
  # number of cards in hand that could be played without taking the lead
  feature_tensor[7, :] = len(loosing_actions) # TODO: exclude trumps
  
  ### features describing the current card
  # value of current card
  for action_index, card in enumerate(valid_actions):
    card_values: torch.Tensor = get_card_values(game_state, hand, feature_tensor, winning_actions, card)
    feature_tensor[8:14, action_index] = card_values
  ### features describing the current leading card
  # number of cards in hand of the same color as current leading card
  feature_tensor[14, :] = len([card for card in hand if card.color == game_state.winning_card.color])
  # number of players playing after current player in current trick
  feature_tensor[15, :] = game_state.n_cards_to_be_played
  # number of cards in current trick
  feature_tensor[16, :] = game_state.n_players - game_state.n_cards_to_be_played
  ### features describing the current leading card
  # whether current leading card is a wizard
  feature_tensor[17, :] = int(game_state.winning_card.value == 14)
  # color of current leading card in trick
  feature_tensor[18, :] = game_state.winning_card.color
  # value of current leading card in trick
  feature_tensor[19, :] = game_state.winning_card.value
  ### features describing the game state
  # serving color
  feature_tensor[20, :] = game_state.serving_color
  # number of tricks needed to match bid
  feature_tensor[21, :] = game_state.players_won_tricks[game_state.trick_active_player] - game_state.players_predictions[game_state.trick_active_player]
  
  return feature_tensor, valid_indices

def get_card_values(
      card: Wizard_Card,
      hand: list[Wizard_Card],
      winning_actions: list[Wizard_Card],
      game_state: Game_State) -> torch.Tensor:
  """
  returns a partial feature vector for a given card

  inputs:
  -------
      card (Wizard_Card): card to be evaluated
      hand (list[Wizard_Card]): list of cards in hand
      winning_actions (list[Wizard_Card]): list of cards that can be played without taking the lead
      game_state (Wizard_Game_State): object representing the current state of the game

  returns:
  --------
      torch.Tensor: partial feature vector for a given card (6 elements)
  """
  feature_vector: torch.Tensor = torch.zeros(6)
  feature_vector[0] = card.value
  # color of current card
  feature_vector[1] = card.color
  # whether current card is a wizard
  feature_vector[2] = int(card.value == 14)
  # whether current card is a trump
  feature_vector[3] = int(card.color == game_state.trump_color)
  # number of cards in hand of the same color as current card
  colored_cards: list[Wizard_Card] = [card for card in hand if card.color == card.color]
  feature_vector[4] = len(colored_cards)
  # whether current leading card can be beaten by a lower card of the same color as the current card
  if len(colored_cards) > 0 and card in winning_actions:
    for colored_card in colored_cards:
      if colored_card.value < card.value and colored_card in winning_actions:
        feature_vector[5] = 1
        break
  return feature_vector



def _get_winning_actions(
      valid_actions: list[Wizard_Card],
      game_state: Game_State) -> tuple[dict[Wizard_Card, float], dict[Wizard_Card, float]]:
    """
    determine which actions are winning and which are loosing

    inputs:
    -------
        valid_actions (list): list of valid actions
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        (list[Wizard_Card]): list of loosing actions
        (list[Wizard_Card]): list of winning actions
    """
    loosing_actions: list[Wizard_Card] = list()
    winning_actions: list[Wizard_Card] = list()
    for action in valid_actions:
      # determine whether an action is winning or not
      _, winning_card, _ = update_winning_card(
          player_index=game_state.trick_active_player,
          new_card=action,
          winner_index=game_state.trick_winner_index,
          winning_card=game_state.winning_card,
          serving_color=game_state.serving_color,
          trump_color=game_state.trump_color)
      # save action and card value in corresponding dict
      if winning_card != action:
        loosing_actions.append(action)
      else:
        winning_actions.append(action)
    return loosing_actions, winning_actions
