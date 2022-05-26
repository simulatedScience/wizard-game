"""
This module implements a Wizard AI that trains using reinforcement learning and self-play.
Techniques like Hindsight Experience Replay may be implemented later.
"""
# import random
import numpy as np
import tensorflow.keras as keras

from pogram_files.wizard_card import Wizard_Card
from pogram_files.wizard_game_state import Wizard_Game_State
from pogram_files.wizard_functions import check_action_invalid
from pogram_files.scoring_functions import update_winning_card


class Basic_NN_Ai():
  name = "basic nn ai"
  def __init__(self):
    self.trump_color_network = self.build_trump_color_network()
    self.bids_predictor_network = self.build_bids_predictor_network()
    self.trick_play_network = self.build_trick_play_network()


  def get_trump_color_choice(self, hands: list, active_player: int, game_state: Wizard_Game_State) -> int:
    """
    choose a trump color based on the current game state
    return color with the most cards

    inputs:
    -------
        active_player (int): index of active player
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        int: integer representing a card color
            0 -> red
            1 -> yellow
            2 -> green
            3 -> blue
    """
    hand = hands[active_player]



  def get_prediction(self, player_index: int, game_state: Wizard_Game_State) -> int:
    """
    predict the number of tricks you expect to win this round based on the current game state
    return predicted number of tricks based on simple rules

    inputs:
    -------
        player_index (int): index of active player
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        int: number of expected won tricks this round
    """
    hand = game_state.players_hands[player_index]


  def get_trick_action(self, game_state: Wizard_Game_State) -> Wizard_Card:
    """
    choose a card to play from the hand based on the current game state
    return a random valid action using a uniform distribution

    inputs:
    -------
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        Wizard_Card: A valid card to be played from the players hand
    """
    hand = game_state.players_hands[game_state.trick_active_player]


  def build_trump_color_network(self):
    """
    generate a neural network that chooses a trump color.
    inputs of the network will be:
    - player's hand -> each card is represented by 2 input neurons
      (maximum of 20 cards in hand, 2 neurons each -> 40 neurons)
    - round number -> 1 neuron
    - number of players -> 1 neuron
    #- (current player scores -> 6 neurons)
    """
    input_size = 40 + 1 + 1
    self.trump_color_network = keras.Sequential()
    self.trump_color_network.compile(optimizer=self.optimizer,
                                     loss=self.loss_function)
