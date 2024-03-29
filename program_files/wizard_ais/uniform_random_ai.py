import random

from program_files.wizard_card import Wizard_Card
from program_files.game_state import Game_State
from program_files.wizard_ais.ai_base_class import Wizard_Base_Ai
from program_files.helper_functions import check_action_invalid


class Uniform_Random_Ai(Wizard_Base_Ai):
  name = "uniform random ai"
  def __init__(self):
    # super().__init__()
    pass


  def get_trump_color_choice(self, hands: list, active_player: int, game_state: Game_State) -> int:
    """
    choose a trump color based on the current game state
    return random card color using uniform distribution

    inputs:
    -------
        player_index (int): index of active player
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        int: integer representing a card color
            0 -> red
            1 -> yellow
            2 -> green
            3 -> blue
    """
    return random.choice((0, 1, 2, 3))


  def get_prediction(self, player_index: int, game_state: Game_State) -> int:
    """
    predict the number of tricks you expect to win this round based on the current game state
    return random number of won tricks using a uniform distribution

    inputs:
    -------
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        int: number of expected won tricks this round
    """
    return random.randint(0, game_state.round_number)


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
      random_action = random.choice(active_set_hand)
      if check_action_invalid(random_action, active_set_hand, game_state.serving_color):
        active_set_hand.remove(random_action)
      else:
        return random_action
