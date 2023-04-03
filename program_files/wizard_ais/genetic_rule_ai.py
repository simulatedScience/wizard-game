import random

import numpy as np

from program_files.wizard_card import Wizard_Card
from program_files.game_state import Game_State
from program_files.wizard_ais.ai_base_class import Wizard_Base_Ai
from program_files.helper_functions import check_action_invalid
from program_files.scoring_functions import update_winning_card


class Genetic_Rule_Ai():
  name = "genetic rule ai"
  def __init__(self):
    raise NotImplementedError


class Genetic_Wizard_Player(Wizard_Base_Ai):
  """
  Define a Wizard AI player that plays according to some basic rules.
  The rules have many adjustable numeric parameters to tweak the behaviour.
  Rules:
  - trump color choice:
      Choose the color that maximizes the following formula (colored_cards are all cards on the player's hand of a given color)
        `color_sum_weight * sum(colored_cards.values) + color_number_weight * n_colored_cards`
  - trick prediction:
      To choose the number of predicted tricks, count the number of non-trump cards with values above `min_value_for_win`,
      add the number of trump cards with values above `min_trump_value_for_win` and add the number of wizards.
      Also add the number of jesters multiplied with `jester_factor`.
      Finally multiply the result by `prediction_factor` and round down to the nearest integer (if that is a valid bid).
      As a formula:
        `int((n_non_trumps * min_value_for_win + n_trumps * min_trump_value_for_win + n_wizards + n_jesters * jester_factor) * prediction_factor)`
  - trick play:
      To choose an action, assign each card on the player's hand a value. If the player still needs to win tricks, play the card with lowest value that still wins,
      otherwise play the card with highest value that still loses. If no card currently loses, play the card with lowest value.
      The value for each card is calculated with the following formula with several parameters:
      Parameters influencing the value are:
        - number of cards of that color (play color with fewest cards first)
        - card value (higher value cards are better)
        - whether card is trump (trump cards are better)
        - how many cards are still to be played (early cards have higher risk, except wizards)
      The formula is:
        `card.value + n_cards_factor * n_cards_of_that_color + trump_value_increase * is_trump + wizard_value * is_wizard + remaining_cards_factor * n_remaining_cards`
  """
        # `base_value = card.value + n_cards_factor * n_cards_of_that_color`
        # `base_value = wizard_value if card is wizard else card.value + trump_value_increase`
  def __init__(self,
      # parameters for trump color choice
      color_sum_weight: float = 0.3,
      color_number_weight: float = 0.7,
      # parameters for bids
      min_value_for_win: float = 10,
      min_trump_value_for_win: float = 7,
      round_factor: float = -0.2,
      jester_factor: float = 0.4,
      prediction_factor: float = 0.9,
      # parameters for trick play
      trump_value_increase: float = 14,
      wizard_value: float = 30,
      n_cards_factor: float = -0.4,
      remaining_cards_factor: float = 0.2,
      ):
    """
    Initialize the AI player with parameters for the rules.

    inputs:
    -------
        # trump color choice parameters
        color_sum_weight (float): Weight for the sum of the values of the cards of a given color.
        color_number_weight (float): Weight for the number of cards of a given color.
        # bid parameters
        min_value_for_win (float): Minimum value for a card to be considered a winning card.
        min_trump_value_for_win (float): Minimum value for a trump card to be considered a winning card.
        round_factor (float): Factor to multiply the number of rounds by to reduce minimum values for winning cards (`min_value_for_win` and `min_trump_value_for_win`). This should be a negative number.
        jester_factor (float): Factor to multiply the number of jesters by to increase the expected number of tricks.
        prediction_factor (float): Factor to multiply the expected number of tricks by to adjust for the risk of other players beating good cards of the player self.
        # trick play parameters
        trump_value_increase (float): Value added to trump cards.
        wizard_value (float): Value for wizards.
        n_cards_factor (float): Factor to multiply the number of cards of a given color by to increase the value of colors with few cards. This should be a negative number.
        remaining_cards_factor (float): Factor to multiply the number of remaining cards in the trick by to decrease the value of cards that are played early. This should be a negative number.
    """
    # trump color choice
    self.color_sum_weight = color_sum_weight
    self.color_number_weight = color_number_weight
    # bids
    self.min_value_for_win = min_value_for_win
    self.min_trump_value_for_win = min_trump_value_for_win
    self.round_factor = round_factor
    self.jester_factor = jester_factor
    self.prediction_factor = prediction_factor
    # trick play
    self.trump_value_increase = trump_value_increase
    self.wizard_value = wizard_value
    self.n_cards_factor = n_cards_factor
    self.remaining_cards_factor = remaining_cards_factor

  def get_trump_color_choice(self, hands: list[Wizard_Card], active_player: int, game_state: Game_State) -> int:
    """
    Choose the trump color based on the current game state.

    Choose the color that maximizes the following formula (colored_cards are all cards on the player's hand of a given color)
      `color_sum_weight * sum(colored_cards.values) + color_number_weight * n_colored_cards`

    inputs:
    -------
        game_state (Game_State): The current game state.

    returns:
    --------
        int: The color to choose as trump. (0: red, 1: yellow, 2: green, 3: blue)
    """
    hand: list[Wizard_Card] = hands[active_player]
    # count the number of cards of each color
    color_counts: dict[int, int] = {}
    color_sums: dict[int, int] = {}
    for card in hand:
      color_counts[card.color] = color_counts.get(card.color, 0) + 1
      color_sums[card.color] = color_sums.get(card.color, 0) + card.value
    # calculate the value for each color
    color_values: dict[int, float] = {}
    for color in color_counts:
      color_values[color] = self.color_sum_weight * color_sums[color] + self.color_number_weight * color_counts[color]
    # choose the color with the highest value
    return max(color_values, key=color_values.get)

  def get_bid(self, game_state: Game_State) -> int:
    """
    Choose the number of predicted tricks based on the current game state.

    To choose the number of predicted tricks, count the number of non-trump cards with values above `min_value_for_win`,
    add the number of trump cards with values above `min_trump_value_for_win` and add the number of wizards.
    Also add the number of jesters multiplied with `jester_factor`.
    Finally multiply the result by `prediction_factor` and round down to the nearest integer (if that is a valid bid).
    As a formula:
      `int((n_non_trumps * min_value_for_win + n_trumps * min_trump_value_for_win + n_wizards + n_jesters * jester_factor) * prediction_factor)`

    inputs:
    -------
        game_state (Game_State): The current game state.

    returns:
    --------
        int: The number of predicted tricks.
    """
    hand: list[Wizard_Card] = game_state.players_hands[game_state.current_player]
    # count the number of non-trump cards with values above `min_value_for_win`
    n_non_trumps: int = len([card for card in hand if card.color != game_state.trump_color and card.value >= self.min_value_for_win])
    # count the number of trump cards with values above `min_trump_value_for_win`
    n_trumps: int = len([card for card in hand if card.color == game_state.trump_color and card.value >= self.min_trump_value_for_win])    
    # count the number of wizards
    n_wizards: int = len([card for card in hand if card.value == 14])
    # count the number of jesters
    n_jesters: int = len([card for card in hand if card.value == 0])
    # calculate the bid
    bid: int = int((n_non_trumps * self.min_value_for_win
               + self.round_factor * game_state.round_number
               + n_trumps * self.min_trump_value_for_win
               + n_wizards + n_jesters * self.jester_factor)
               * self.prediction_factor)
    # make sure bid is valid
    if bid < 0:
      print(f"Warning: bid is negative: {bid}")
      bid: int = 0
    elif bid > game_state.round_number:
      print(f"Warning: bid is too high: {bid}")
      bid: int = game_state.round_number
    return bid

  def get_trick_action(self, game_state: Game_State) -> Wizard_Card:
    """
    Choose the card to play based on the current game state.

    To choose an action, assign each card on the player's hand a value. If the player still needs to win tricks, play the card with lowest value that still wins,
    otherwise play the card with highest value that still loses. If no card currently loses, play the card with lowest value.
    The value for each card is calculated with the following formula with several parameters:
    Parameters influencing the value are:
      - number of cards of that color (play color with fewest cards first)
      - card value (higher value cards are better)
      - whether card is trump (trump cards are better)
      - how many cards are still to be played (early cards have higher risk, except wizards)
    The values are calculated as follows:
      `card.value + n_cards_factor * n_cards_of_that_color + trump_value_increase * is_trump + wizard_value * is_wizard + remaining_cards_factor * n_remaining_cards`

    inputs:
    -------
        game_state (Game_State): The current game state.

    returns:
    --------
        Wizard_Card: The card to play.
    """
    hand: list[Wizard_Card] = game_state.players_hands[game_state.current_player]
    # count the number of cards of each color
    color_counts: dict[int, int] = {}
    for card in hand:
      color_counts[card.color] = color_counts.get(card.color, 0) + 1
    # calculate the value for each card
    valid_actions = [card for card in hand if not check_action_invalid(card, hand, game_state.serving_color)]
    card_values: list[float] = [0] * len(valid_actions)
    for card_index, card in enumerate(valid_actions): # only score valid actions
      card_values[card_index] = (card.value
          + self.n_cards_factor * color_counts[card.color]
          + self.trump_value_increase * (card.color == game_state.trump_color)
          + self.wizard_value * (card.value == 14)
          + self.remaining_cards_factor * game_state.cards_to_be_played)
    loosing_actions, winning_actions = self._get_winning_actions(valid_actions, card_values, game_state)
    
    # choose the action
    if game_state.players_won_tricks[game_state.trick_active_player] < game_state.players_predictions[game_state.trick_active_player]:
      # player still needs to win tricks
      if winning_actions:
        # play the card with lowest value that still wins
        return min(winning_actions, key=card_values.get)
      else:
        # play the card with lowest value
        return min(valid_actions, key=card_values.get)
    else:
      # player does not need to win tricks anymore
      if loosing_actions:
        # play the card with highest value that still loses
        return max(loosing_actions, key=card_values.get)
      else:
        # play the card with lowest value
        return min(valid_actions, key=card_values.get)

  def _get_winning_actions(self,
      valid_actions: list[Wizard_Card],
      card_values: list[float],
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


  def __str__(self) -> str:
    return "Genetic_Wizard_Ai with parameters:\n  " + "\n  ".join([f"{param_name}: {value}" for param_name, value in self.__dict__.items()])

  # methods for genetic algorithm
  def mutate(self, mutation_rate: float = 0.1) -> None:
    """
    Mutate the agent's parameters.
    Mutations are done by adding a random value between -1 and 1 to the parameter.

    inputs:
    -------
        mutation_rate (float): probability of mutation
    """
    new_parameters: dict[str, float] = {}
    for param_name, value in self.__dict__.items():
      if random.random() < mutation_rate:
        new_parameters[param_name] = value + random.uniform(-1, 1)
      else:
        new_parameters[param_name] = value
    self.__dict__ = new_parameters

  def crossover(self, other: "Genetic_Rule_Ai", combination_range: float = 0.5) -> "Genetic_Rule_Ai":
    """
    Create a new agent by crossing over the parameters of two agents.
    Recombination is done by considering the distance between the two parents' parameters and then choosing a random value between the two parents' parameters or outside of their range by a factor of `combination_range`.

    inputs:
    -------
        other (Genetic_Rule_Ai): other agent
        combination_range (float): factor how many distances between the two parent's parameter the child's parameter can be outside of their range. 0 means the child's parameter is a random one between the two parents, 1 means the child's parameter can be at most |parent_1_param - parent_2_param| away from the either parent's parameter.

    returns:
    --------
        Genetic_Rule_Ai: new AI with parameters derived from the two parents
    """
    new_params = {}
    other_params = other.__dict__
    for param_name, value in self.__dict__.items():
      distance: float = other_params[param_name] - value
      random_factor: float = random.random() * (1 + 2 * combination_range * distance) - combination_range * distance
      new_params[param_name]: float = value + random_factor * distance
    return Genetic_Wizard_Player(**new_params)
