"""
this module implements a base class for any AI for the wizard game.
"""


from wizard_card import Wizard_Card
from wizard_game_state import Wizard_Game_State


class Wizard_Base_Ai():
  def __init__(self):
    # self.name = name
    pass


  def get_trump_color_choice(self, hands: list, game_state: Wizard_Game_State) -> int:
    """
    choose a trump color based on the current game state

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
    raise NotImplementedError("Trump color choice has not been implemented for this AI.")


  def get_prediction(self, game_state: Wizard_Game_State) -> int:
    """
    predict the number of tricks you expect to win this round based on the current game state

    inputs:
    -------
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        int: number of expected won tricks this round
    """
    raise NotImplementedError("Bids prediction has not been implemented for this AI.")


  def get_trick_action(self, game_state: Wizard_Game_State) -> Wizard_Card:
    """
    choose a card to play from the hand based on the current game state

    inputs:
    -------
        game_state (Wizard_Game_State): object representing the current state of the game

    returns:
    --------
        Wizard_Card: A valid card to be played from the players hand
    """
    raise NotImplementedError("Trick play has not been implemented for this AI.")
