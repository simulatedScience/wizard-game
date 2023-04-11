"""
This module implements a Wizard AI that uses a neural network to make decisions. The NNs weights are optimized using a genetic algorithm.
The NNs input is a condensed representation of the game state. The output is a value for each possible action. The action with the highest value will then be chosen (greedy policy).

feature vectors are defined in `wizard_feature_vectors.py`.
"""
import os
import random

import numpy as np
import torch

from program_files.game_state import Game_State
from program_files.wizard_card import Wizard_Card
from program_files.wizard_ais.ai_base_class import Wizard_Base_Ai
from program_files.wizard_ais.wizard_feature_vectors import get_trump_choice_features, get_prediction_features, get_trick_action_features
from program_files.wizard_ais.pytorch_dense_nn import Dense_NN


class Genetic_NN_Ai(Wizard_Base_Ai):
  """
  This class implements a Wizard AI that uses a neural network to make decisions. The NNs weights are optimized using a genetic algorithm.
  The NNs layout is fixed during training. The NNs input is a condensed representation of the game state. The output is a value for each possible action. The action with the highest value will then be chosen (greedy policy).
  """
  name = "genetic_nn_ai"
  def __init__(self):
    """
    initialize the neural networks by loading them from file
    """
    base_path: str = os.path.join("program_files", "wizard_ais", "genetic_nn_ai")
    self.trick_action_nn: torch.nn.Module = torch.load(os.path.join(base_path, "trick_action_nn.pt"))
    self.trump_color_nn: torch.nn.Module = torch.load(os.path.join(base_path, "trump_color_nn.pt"))
    self.prediction_nn: torch.nn.Module = torch.load(os.path.join(base_path, "prediction_nn.pt"))

  def get_trump_color_choice(self,
      hands: list[list[Wizard_Card]],
      active_player: int,
      game_state: Game_State) -> int:
    """
    choose a trump color based on the current game state
    return color based on the neural network's output.

    inputs:
    -------
        hands  list[list[Wizard_Card]]): list of cards in hand of the active player
        active_player (int): integer representing the active player index
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        int: integer representing a card color
            0 -> red
            1 -> yellow
            2 -> green
            3 -> blue
    """
    hand: list[Wizard_Card] = hands[active_player]


class Genetic_NN_Player(Wizard_Base_Ai):
  """
  This class implements a parametrized version of the Genetic_NN_Ai class. It allows to create multiple instances of the Genetic_NN_Ai class with different weights and provides methods to mutate and crossover the weights.
  """
  def __init__(self,
        trump_color_nn_leyers: list[int],
        trump_color_nn_weights: list[torch.Tensor],
        prediction_nn_layers: list[int],
        prediction_nn_weights: list[torch.Tensor],
        trick_action_nn_layers: list[int],
        trick_action_nn_weights: list[torch.Tensor]):
    """
    initialize the neural networks by loading them from file
    """
    self.trump_color_nn: torch.nn.Module = Dense_NN(
        22, 4, trump_color_nn_leyers)
    self.trump_color_nn.set_weights(trump_color_nn_weights)
    self.prediction_nn: torch.nn.Module = Dense_NN(
        22, 1, prediction_nn_layers)
    self.prediction_nn.set_weights(prediction_nn_weights)
    self.trick_action_nn: torch.nn.Module = Dense_NN(
        22, 1, trick_action_nn_layers)
    self.trick_action_nn.set_weights(trick_action_nn_weights)


  def get_trump_color_choice(self,
      hands: list[list[Wizard_Card]],
      active_player: int,
      game_state: Game_State) -> int:
    """
    choose a trump color based on the current game state
    return color based on the neural network's output.

    inputs:
    -------
        hands  list[list[Wizard_Card]]): list of cards in hand of the active player
        active_player (int): integer representing the active player index
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        int: integer representing a card color
            0 -> red
            1 -> yellow
            2 -> green
            3 -> blue
    """
    features: torch.Tensor = get_trump_choice_features(hands, active_player, game_state)
    # get the output of the neural network
    output: torch.Tensor = self.trump_color_nn(features)
    # get the index of the highest value in the output tensor
    color_index: int = torch.argmax(output).item()
    return color_index
  
  def get_prediction(self, player_index: int, game_state: Game_State) -> int:
    """
    get the prediction of the given player based on the internal neural network for bid prediction.

    Args:
        player_index (int): index of the player
        game_state (Game_State): current game state

    Returns:
        int: the predicted bid
    """
    features: torch.Tensor = get_prediction_features(player_index, game_state)
    # get the output of the neural network
    output: torch.Tensor = self.prediction_nn(features)
    # get the index of the highest value in the output tensor
    prediction: int = torch.argmax(output).item()
    return prediction
  
  def get_trick_action(self, game_state: Game_State) -> Wizard_Card:
    """
    choose a card to play based on the current game state
    return card based on the neural network's output.

    inputs:
    -------
        hands  list[list[Wizard_Card]]): list of cards in hand of the active player
        active_player (int): integer representing the active player index
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        Wizard_Card: card to play
    """
    features: torch.Tensor = get_trick_action_features(game_state)
    # get the output of the neural network for each possible action
    output: torch.Tensor = self.trick_action_nn(features)
    # get the index of the highest value in the output tensor
    action_index: int = torch.argmax(output).item()
    return game_state.players_hands[game_state.trick_active_player][action_index]

