"""
this module includes
"""
from typing import Tuple
from program_files.wizard_card import Wizard_Card
import numpy as np


def update_winning_card(
        player_index: int,
        new_card: Wizard_Card,
        winner_index: int,
        winning_card: Wizard_Card,
        serving_color: int,
        trump_color: int) -> Tuple[int, Wizard_Card, int]:
  """
  Update the winning card in a trick by checking whether it is better than the previosly best card `winning_card`

  inputs:
  -------
      player_index (int) - index of the player who played the new card.
      new_card (Wizard_Card) - newly played card.
      winner_index (int) - index of the player who played the winning card.
      winning_card (Wizard_Card) - previously best card in this trick. `None` if no card was played yet.
      serving_color (int) - color index that needs to be served.
      trump_color (int) - color index of the trump card. ´None` if there is no trump.

  returns:
  --------
      (int) - winner index: index of the player who played the winning card.
      (Wizard_Card) - winning card: best card in this trick.
      (int) - serving color: color index that needs to be served.
  """
  # first played card is always the best so far
  if winning_card is None:
    winner_index = player_index
    winning_card = new_card
    if new_card.color != -1:
      serving_color = new_card.color
  elif new_card.value == 0: # jester was played after first card
    return winner_index, winning_card, serving_color
  # first card other than jester determines serving color
  elif winning_card.value == 0 and new_card.color != -1:
    winner_index = player_index
    winning_card = new_card
    serving_color = new_card.color
  # check if new_card is wizard -> wins if winning_card is not a wizard
  elif new_card.value == 14 and winning_card.value < 14:
    if winning_card.value == 0:
      serving_color = new_card.color
    winner_index = player_index
    winning_card = new_card
  elif new_card.value == 14: # wizard was played but doesn't win
    return winner_index, winning_card, serving_color
  # trump card wins over all non-trump cards
  elif new_card.color == trump_color \
          and winning_card.color != trump_color \
          and 0 < winning_card.value < 14:
    # print(trump_color, new_card)
    winner_index = player_index
    winning_card = new_card
    # print("Rule 4: trump")
  # check regular card and (trump card if current winner is trump)
  elif new_card.color == winning_card.color and new_card.value > winning_card.value:
    winner_index = player_index
    winning_card = new_card
    # print("Rule 5: regular card")
  # print(winner_index, winning_card, serving_color)
  return winner_index, winning_card, serving_color


def score_trick(played_cards: list[Wizard_Card], trump: int) -> int:
  """
  calculate the winner at the end of a given trick.
  - The Jester always loses unless there are only jesters played. Then the first player wins.
  - The first played wizard always wins.
  - Any trump cards are always better than non-trump.
  - Higher card values win over lower ones.
  - no trump can be given by setting trump to anything other than 0,1,2 and 3.

  inputs:
  -------
      player_cards (list) of (Wizard_Card) - list of played cards
      trump (int) - trump for the played round

  returns:
  --------
      (int) - index of the player who won the given trick
  """
  winner = 0
  winning_card = played_cards[0]
  if winning_card.value == 14:
    return winner # first player won with wizard
  for i, card in enumerate(played_cards[1:]):
    # check wizard
    if card.value == 14 and winning_card.value < 14:
      return i + 1
    # check if winning card is jester
    if winning_card.value == 0 and card.value > 0:
      winner = i + 1
      winning_card = card
      continue
    # check jester
    if card.value == 0:
      continue
    assert card.color != -1
    # check trump card when current winner is not trump
    if card.color == trump and winning_card.color != trump:
      winner = i + 1
      winning_card = card
      continue
    # check regular card and (trump card if current winner is trump)
    if card.color == winning_card.color and card.value > winning_card.value:
      winner = i + 1
      winning_card = card
  return winner


def score_round(predictions, won_tricks):
  """
  calculate how many points each player should get for a played round

  scoring:
      +20 if number of tricks matches prediction
      +10 for every correctly predicted trick (only if number of tricks matches prediction)
      -10*(difference between predicted and won tricks)

  inputs:
  -------
      predictions (np.ndarray) - array containing the predicted number of tricks of each player
      won_tricks (np.ndarray) - array containing how many tricks each player actually won
  """
  correctly_guessed = predictions == won_tricks
  scores = correctly_guessed * 20 \
      + 10 * correctly_guessed * won_tricks \
      - 10 * np.abs(predictions - won_tricks)
  return scores
