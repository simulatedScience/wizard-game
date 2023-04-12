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
  # methods for playing
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
    features, valid_indices = get_trick_action_features(game_state)
    # get the output of the neural network for each possible action
    output: torch.Tensor = self.trick_action_nn(features)
    # get the index of the highest value in the output tensor
    action_index: int = torch.argmax(output).item()
    action_index: int = valid_indices[action_index]
    return game_state.players_hands[game_state.trick_active_player][action_index]


class Genetic_NN_Player(Wizard_Base_Ai):
  """
  This class implements a parametrized version of the Genetic_NN_Ai class. It allows to create multiple instances of the Genetic_NN_Ai class with different weights and provides methods to mutate and crossover the weights.
  """
  def __init__(self,
        trump_color_nn_layers: tuple[int],
        prediction_nn_layers: tuple[int],
        trick_action_nn_layers: tuple[int],
        trump_color_nn_weights: list[torch.Tensor] = None,
        prediction_nn_weights: list[torch.Tensor] = None,
        trick_action_nn_weights: list[torch.Tensor] = None):
    """
    initialize the neural networks by loading them from file
    """
    # trump color choice nn
    self.trump_color_nn_layers: tuple[int] = trump_color_nn_layers
    self.trump_color_nn: torch.nn.Module = Dense_NN(
        18, 4, trump_color_nn_layers)
    if trump_color_nn_weights is not None:
      self.trump_color_nn.set_weights(trump_color_nn_weights)
    # prediction nn
    self.prediction_nn_layers: tuple[int] = prediction_nn_layers
    self.prediction_nn: torch.nn.Module = Dense_NN(
        20, 1, prediction_nn_layers)
    if prediction_nn_weights is not None:
      self.prediction_nn.set_weights(prediction_nn_weights)
    # trick action nn
    self.trick_action_nn_layers: tuple[int] = trick_action_nn_layers
    self.trick_action_nn: torch.nn.Module = Dense_NN(
        22, 1, trick_action_nn_layers)
    if trick_action_nn_weights is not None:
      self.trick_action_nn.set_weights(trick_action_nn_weights)

  def save(self, save_dir: str = None):
    """
    save the neural networks weights to file

    Args:
        save_dir (str): directory to save the weights to
    """
    if save_dir is None:
      save_dir = os.path.join("program_files", "wizard_ais", "genetic_nn_ai")
    torch.save(self.trump_color_nn, os.path.join(save_dir, "trump_color_nn.pt"))
    torch.save(self.prediction_nn, os.path.join(save_dir, "prediction_nn.pt"))
    torch.save(self.trick_action_nn, os.path.join(save_dir, "trick_action_nn.pt"))

  # methods for playing
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
    features, valid_indices = get_trick_action_features(game_state)
    # get the output of the neural network for each possible action
    output: torch.Tensor = self.trick_action_nn(features)
    # get the index of the highest value in the output tensor
    action_index: int = torch.argmax(output).item()
    action_index: int = valid_indices[action_index]
    return game_state.players_hands[game_state.trick_active_player][action_index]

  # methods for the genetic algorithm
  def mutate(self, mutation_rate: float = 0.1, mutation_range: float = 0.1) -> None:
    """
    Mutate the neural network weights of the agent by adding a random value to each parameter.
    The random value is chosen from a normal distribution with a mean of 0 and a standard deviation of `mutation_range`.

    inputs:
    -------
        mutation_range (float): standard deviation of the normal distribution from which the mutation is chosen
    """
    for network_name in ("trump_color_nn", "prediction_nn", "trick_action_nn"):
      network: Dense_NN = getattr(self, network_name)
      weights: list[torch.Tensor] = network.get_weights()
      for i, weight_tensor in enumerate(weights):
        if random.random() < mutation_rate:
          # get the mutation value from a normal distribution
          mutation: torch.Tensor = torch.normal(1, mutation_range, size = weight_tensor.shape)
          weights[i]: torch.Tensor = weight_tensor * mutation
      network.set_weights(weights)

  def crossover(self, other: "Genetic_NN_Player", combination_range: float = 0.1) -> "Genetic_NN_Player":
    """
    Create a new agent by crossing over the neural network weights of two agents.
    Recombination is done by considering the distance between the two parents' parameters and then choosing a random value between the two parents' parameters or outside of their range by a factor of `combination_range`.

    inputs:
    -------
        other (Genetic_Rule_Ai): other agent
        combination_range (float): factor how many distances between the two parent's parameter the child's parameter can be outside of their range. 0 means the child's parameter is a random one between the two parents, 1 means the child's parameter can be at most |parent_1_param - parent_2_param| away from the either parent's parameter.

    returns:
    --------
        Genetic_Rule_Ai: new AI with parameters derived from the two parents
    """
    child_network_parameters: dict[str, list[torch.Tensor]] = {}
    for network_name in ("trump_color_nn", "prediction_nn", "trick_action_nn"):
      parent_1_network: Dense_NN = getattr(self, network_name)
      parent_2_network: Dense_NN = getattr(other, network_name)
      parent_1_weights: list[torch.Tensor] = parent_1_network.get_weights()
      parent_2_weights: list[torch.Tensor] = parent_2_network.get_weights()
      child_network_parameters[network_name+"_weights"]: list[torch.Tensor] = []
      for weight_tensor_1, weight_tensor_2 in zip(parent_1_weights, parent_2_weights):
        # get the distance between the two parents' parameters
        distance: torch.Tensor = weight_tensor_1 - weight_tensor_2
        random_factor: float = random.random() * (1 + 2 * combination_range * distance) - combination_range * distance
        new_weights: torch.Tensor = weight_tensor_1 + random_factor * distance
        child_network_parameters[network_name+"_weights"].append(new_weights)
    return Genetic_NN_Player(
      trump_color_nn_layers = self.trump_color_nn_layers,
      prediction_nn_layers = self.prediction_nn_layers,
      trick_action_nn_layers = self.trick_action_nn_layers,
      **child_network_parameters)

  def get_parameters(self) -> dict[str, list[torch.Tensor]]:
    """
    get the parameters of the neural networks of the agent

    returns:
    --------
        dict[str, list[torch.Tensor]]: dictionary with the parameters of the three neural networks
    """
    return {
      "trump_color_nn_weights": self.trump_color_nn.get_weights(),
      "prediction_nn_weights": self.prediction_nn.get_weights(),
      "trick_action_nn_weights": self.trick_action_nn.get_weights()
    }