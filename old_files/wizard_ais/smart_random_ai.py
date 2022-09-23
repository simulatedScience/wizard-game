# import random
import numpy as np

from program_files.wizard_card import Wizard_Card
from program_files.game_state import Game_State
from program_files.helper_functions import check_action_invalid
# from .ai_base_class import Wizard_Base_Ai


class Smart_Random_Ai():
  name = "smart random ai"
  def __init__(self):
    # super().__init__()
    pass


  def get_trump_color_choice(self, hands: list, active_player: int, game_state: Game_State) -> int:
    """
    choose a trump color based on the current game state
    return random card color weighted with the sum of card values from each color

    inputs:
    -------
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
    # calculate weights for each color
    color_weights = np.zeros(4, dtype=np.float64)
    for i, _ in enumerate(color_weights):
      color_weights[i] = sum([card.value for card in hand if card.color == i])
    s = np.sum(color_weights)
    if s == 0:  # choose uniform random color if no card on hand has a color
      return np.random.choice((0, 1, 2, 3))
    color_weights /= np.sum(color_weights)
    return np.random.choice((0, 1, 2, 3), p=color_weights)


  def get_prediction(self, player_index: int, game_state: Game_State) -> int:
    """
    predict the number of tricks you expect to win this round based on the current game state
    return random number of won tricks using a uniform distribution

    inputs:
    -------
        player_index (int): index of active player
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        int: number of expected won tricks this round
    """
    random_bid = round(np.random.normal(
        loc=game_state.round_number / game_state.n_players,
        scale=game_state.round_number / game_state.n_players / 5))
    if random_bid < 0:
      return 0
    if random_bid > game_state.round_number:
      return game_state.round_number
    return random_bid


  def get_trick_action(self, game_state: Game_State) -> Wizard_Card:
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
    active_set_hand = game_state.players_hands[game_state.trick_active_player].copy()
    while True:
      card_weights = np.array([card.value for card in active_set_hand], dtype=np.float64)
      weight_total = np.sum(card_weights)
      if weight_total == 0:  # only jesters on hand -> always valid action
        return np.random.choice(active_set_hand)

      # Check whether the AI still needs to win tricks. If not, prefer playing lower cards
      if game_state.players_predictions[game_state.trick_active_player] >= game_state.players_won_tricks[game_state.trick_active_player]:
        card_weights = 15 - card_weights  # higher cards are less likely to be played
        weight_total = np.sum(card_weights)
      card_weights /= weight_total

      # choose a random action based on weights, if it's invalid, choose again.
      random_action = np.random.choice(active_set_hand, p=card_weights)
      if check_action_invalid(random_action, active_set_hand, game_state.serving_color):
        active_set_hand.remove(random_action)
      else:
        return random_action
