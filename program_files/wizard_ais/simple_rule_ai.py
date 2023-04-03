# import random
import numpy as np

from program_files.wizard_card import Wizard_Card
from program_files.game_state import Game_State
from program_files.wizard_ais.ai_base_class import Wizard_Base_Ai
from program_files.helper_functions import check_action_invalid
from program_files.scoring_functions import update_winning_card


class Simple_Rule_Ai(Wizard_Base_Ai):
  name = "simple rule ai"
  def __init__(self):
    # super().__init__()
    self.trump_shift = 14
    self.wizard_value = 30
    self.prediction_factor = 0.8
    self.min_value_for_win = 10
    self.min_trump_value_for_win = 8


  def get_trump_color_choice(self, hands: list, active_player: int, game_state: Game_State) -> int:
    """
    choose a trump color based on the current game state
    return color with the most cards

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
      color_weights[i] = len([card for card in hand if card.color == i])
    total_weights = np.sum(color_weights)
    if total_weights == 0:  # choose uniform random color if no card on hand has a color
      return np.random.choice((0, 1, 2, 3))
    return np.argmax(color_weights)


  def get_prediction(self, player_index: int, game_state: Game_State) -> int:
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
    prediction = 0
    for card in game_state.players_hands[player_index]:
      if card.value >= self.min_value_for_win:
        prediction += 1
      elif card.color == game_state.trump_color \
              and card.value >= self.min_trump_value_for_win:
        prediction += 1
    return round(prediction * self.prediction_factor)


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
    hand = game_state.players_hands[game_state.trick_active_player]
    valid_actions = [card for card in hand if not check_action_invalid(card, hand, game_state.serving_color)]
    card_values = self._get_card_values(valid_actions, game_state)
    loosing_actions, winning_actions = self._get_winning_actions(
        valid_actions,
        card_values,
        game_state)

    # Check whether the AI still needs to win tricks. If not, prefer playing lower cards
    wanted_tricks = game_state.players_predictions[game_state.trick_active_player]
    current_tricks = game_state.players_won_tricks[game_state.trick_active_player]
    # no more tricks wanted
    if wanted_tricks >= current_tricks:
      action = self._choose_action(loosing_actions, "high")
      if action is None:
        self._choose_action(winning_actions, "high")
    # win last wanted trick
    if wanted_tricks == current_tricks + 1:
      action = self._choose_action(winning_actions, "high")
      if action is None:
        action = self._choose_action(loosing_actions, "low")

    else:
      action = self._choose_action(winning_actions, "low")
      if action is None:
        action = self._choose_action(loosing_actions, "low")

    return action


  def _choose_action(self, action_list, sub_selection_mode: str = "high"):
    if len(action_list) == 0:
      return None
    if sub_selection_mode == "high":
      return max(action_list, key=action_list.get)
    # choose lowest value action
    return min(action_list, key=action_list.get)


  def _get_winning_actions(self,
      valid_actions: list,
      card_values: list,
      game_state: Game_State):
    """
    determine which actions are winning and which are loosing

    inputs:
    -------
        valid_actions (list): list of valid actions
        card_values (list): list of values for each valid action
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        (dict): dictionary of loosing actions and their values
        (dict): dictionary of winning actions and their values
    """
    if game_state.cards_to_be_played == game_state.get_state_dict:
      # all actions win.
      return list(), valid_actions
    loosing_actions = dict()
    winning_actions = dict()
    for action, value in zip(valid_actions, card_values):
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
        loosing_actions[action] = value
      else:
        winning_actions[action] = value
    return loosing_actions, winning_actions


  def _get_card_values(self, actions: list, game_state: Game_State):
    """
    assign values to each available action based on the current game state.
    Wizards have maximum value, jesters minimum value.
    Any trump card is worth more than any non-trump card.

    inputs:
    -------
        actions (list): list of Wizard cards
        game_state ([type]): [description]
    """
    card_values = list()
    for card in actions:
      if card.color == game_state.trump_color:  # trump cards
        card_values.append(card.value + self.trump_shift)
      elif card.value == 14:  # wizards
        card_values.append(self.wizard_value)
      else:  # non-trump cards and jesters
        card_values.append(card.value)
    return card_values
