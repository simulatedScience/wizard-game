from game_state import Game_State

class Game_Engine:
  def __init__(self, n_players: int, verbosity: int = 0):
    """this class handles all the game logic during play

    Args:
        n_players (int): number of players
        verbosity (int, optional): verbosity = how much text output to give. Defaults to 0 meaning no output except in case of fatal errors. Higher values indicate more output.
    """
    self.n_players = n_players
    self.verbosity = verbosity

    self.next_function_call: callable = self._start_game
    self.next_event: str = "start game"

  def _start_game(self):
    """start a game"""
    self.game_obj = Game_State(self.n_players, self.verbosity)



  def _start_round(self):
    """start a round"""

  def _start_trick(self):
    """start a trick"""