import numpy as np

from program_files.wizard_card import Wizard_Card
from program_files.scoring_functions import update_winning_card, score_round


class Game_State():
  """
  This class stores all relevant information about the current state of a Wizard game.

  This includes:
      - number of players - (int) - `n_players`
      - round number - (int) - `round_number`
      - round starting player - (int) - `round_starting_player` - `<= n_players`
      - tricks to be played - (int) - `tricks_to_be_played` - `<= round_number`
      - trick starting player - (int) - `trick_starting_player` - `<= n_players`
      - player hands - (list[list[Wizard_Card]]) - `players_hands`
      - predictions for each player - (list[int]) - `players_predictions`
      - won tricks for each player - (list[int]) - `players_won_tricks`
      - total points for each player - (list[int]) - `players_total_points`
      - public card states - (list[int]) - `public_card_states`
  """
  def __init__(self, n_players: int, verbosity: int = 0):
    self.n_players: int = n_players
    self.verbosity: int = verbosity

    self.round_number = 1
    self.round_starting_player = np.random.randint(n_players)
    self.trump_card: Wizard_Card = None
    self.trump_color: int = -1  # -1 = no trump

    self.tricks_to_be_played: int = 1
    self.trick_active_player = self.round_starting_player
    self.trick_winner_index: int = 0

    self.cards_to_be_played: int = n_players
    self.winning_card: Wizard_Card = None
    self.serving_color: int = None

    self.players_hands: set = None
    self.players_predictions: "np.ndarray" = None
    self.players_won_tricks: "np.ndarray" = np.zeros(n_players, dtype=np.int8)
    self.players_gained_points_history: "np.ndarray" = np.zeros((60 // n_players, n_players))
    self.players_total_points: "np.ndarray" = np.zeros(n_players, dtype=np.int16)

    self.public_card_states: "np.ndarray" = -np.ones(60, dtype=np.int8)


  def perform_action(self, action: Wizard_Card) -> None:
    """
    Perform an action and update all game state variables accordingly.
    Automatically starts the next trick or round if necessary.
    If `self.verbosity` is at least 2, print the action.

    (potentially) updated variables:
        - players_hands
        - trick_active_player
        - cards_to_be_played
        - trick_winner_index
        - winning_card
        - serving_color
        - public_card_states
        variables updated by `next_trick` and `next_round`

    inputs:
    -------
        action (Wizard_Card): a card in the hand of the active player. `perform_action` does NOT check, whether this action is valid but assumes it is. Behaviour for invalid actions is undefined.
    """
    self.players_hands[self.trick_active_player].remove(action)
    self.public_card_states[action.raw_value] = self.trick_active_player
    if self.verbosity >= 2:
      print(f"player P{self.trick_active_player+1} played card {action}.")
    self.trick_winner_index, self.winning_card, self.serving_color = \
        update_winning_card(
            player_index=self.trick_active_player,
            new_card=action,
            winner_index=self.trick_winner_index,
            winning_card=self.winning_card,
            serving_color=self.serving_color,
            trump_color=self.trump_color)
    # increment active player index
    self.trick_active_player = (self.trick_active_player + 1) % self.n_players
    # increment cards left to be played in the current trick
    if self.cards_to_be_played > 1:  # last card was played
      self.cards_to_be_played -= 1
      return_val = 0
    else:
      self._end_trick()
      return_val = 1
    if self.tricks_to_be_played == 0:
      self._end_round()
      return_val = 2
    return return_val


  def start_trick(self) -> bool:
    """
    Start the next trick and updates game state variables accordingly.
    If `self.verbosity` is at least 1, print the winner of the trick.

    updated variables:
        - players_won_tricks
        - tricks_to_be_played
        - trick_active_player
        - trick_winner_index
        - cards_to_be_played
        - winning_card
        - serving_color
        variables updated by `next_round`

    returns:
    --------
        (bool) - whether or not this was the last trick in the round
    """
    # reset variables for next trick
    self.trick_winner_index = 0

    self.cards_to_be_played: int = self.n_players
    self.winning_card: Wizard_Card = None
    self.serving_color: int = None


  def _end_trick(self):
    """
    score the last played trick. This method is automatically executed after the last action of a trick.
    """
    # assign one won trick to winning player
    self.players_won_tricks[self.trick_winner_index] += 1
    if self.verbosity >= 1:
      print(f"player P{self.trick_winner_index+1} won the trick with {self.winning_card}")
    # increment trick counter
    self.tricks_to_be_played -= 1
    # update trick starting player
    self.trick_active_player: int = self.trick_winner_index


  def start_round(self, hands, trump_card, trump_color):
    """
    Start the next round and update game state variables accordingly.
    If `self.verbosity` is at least 1, print the winner of the round.

    updated variables:
        - round_number
        - round_starting_player
        - trump_card
        - trump_color
        - tricks_to_be_played
        - trick_active_player
        - players_hands
        - players_total_points
        - players_predictions
        - players_won_tricks
        - public_card_states
    """
    self.round_starting_player = (self.round_starting_player + 1) % self.n_players
    # set trump information
    self.trump_card = trump_card
    self.trump_color = trump_color
    # set trick information
    self.tricks_to_be_played = self.round_number
    self.trick_active_player = self.round_starting_player
    # set player information
    self.players_hands = hands
    self.players_predictions = None
    self.players_won_tricks = np.zeros(self.n_players, dtype=np.int8)
    # set card state information
    self.public_card_states = -np.ones(60, dtype=np.int8)
    if trump_card != None:
      self.public_card_states[trump_card.raw_value] = -2  # trump card


  def _end_round(self):
    """
    Score the last played round. This method is automatically executed after the last trick of a round was played.
    """
    # calculate points earned this round
    round_points = score_round(self.players_predictions, self.players_won_tricks)
    # save points in history
    self.players_gained_points_history[self.round_number - 1, :] = round_points
    # add points to totals
    self.players_total_points += round_points
    # increment round number
    self.round_number += 1


  def set_predictions(self, predictions: "np.ndarray"):
    """
    save predictions

    inputs:
    -------
        predictions (np.ndarray): predicted number of tricks for each player
    """
    self.players_predictions = predictions

  def get_active_player_hand(self) -> list:
    """returns the hand of the active player

    Returns:
        list: _description_
    """
    self.players_hands

  def get_state_dict(self) -> dict:
    state_dict = {
        "n_players": self.n_players,

        "round_number": self.round_number,
        "round_starting_player": self.round_starting_player,
        "trump_card": self.trump_card,
        "trump_color": self.trump_color,

        "tricks_to_be_played": self.tricks_to_be_played,
        "trick_active_player": self.trick_active_player,
        "trick_winner_index": self.trick_winner_index,

        "cards_to_be_played": self.cards_to_be_played,
        "winning_card": self.winning_card,
        "serving_color": self.serving_color,

        "players_hands": self.players_hands,
        "players_predictions": self.players_predictions,
        "players_won_tricks": self.players_won_tricks,
        "players_gained_points_history": self.players_gained_points_history,
        "players_total_points": self.players_total_points,

        "public_card_states": self.public_card_states
    }
    return state_dict
