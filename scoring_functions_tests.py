"""
test scoring functions for wizard game
"""

from program_files.game_state import Game_State
from program_files.wizard_card import Wizard_Card
from program_files.scoring_functions import update_winning_card, score_trick, score_round

def test_wizard_tricks():
  """
  test trick scoring in different scenarios where a wizard is played
  - wizard played first
  - wizard played after winning trump card
  - wizard played after another wizard
  - wizard played after jesters
  """
  played_cards: list[Wizard_Card] = [
    Wizard_Card( 1), # red 1
    Wizard_Card(14), # red wizard
    Wizard_Card(17), # yellow 2
  ]
  for trump in range(4):
    assert score_trick(played_cards, trump=trump) == 1
  
  played_cards: list[Wizard_Card] = [
    Wizard_Card( 1), # red 1
    Wizard_Card(17), # yellow 2
    Wizard_Card(14), # red wizard
  ]
  for trump in range(4):
    assert score_trick(played_cards, trump=trump) == 2

  played_cards: list[Wizard_Card] = [
    Wizard_Card( 1), # red 1
    Wizard_Card(29), # yellow wizard
    Wizard_Card(14), # red wizard
  ]
  for trump in range(4):
    assert score_trick(played_cards, trump=trump) == 1

  played_cards: list[Wizard_Card] = [
    Wizard_Card(29), # yellow wizard
    Wizard_Card(13), # red 13
    Wizard_Card(14), # red wizard
  ]
  for trump in range(4):
    assert score_trick(played_cards, trump=trump) == 0

  played_cards: list[Wizard_Card] = [
    Wizard_Card(15), # yellow jester
    Wizard_Card(23), # yellow 8
    Wizard_Card(30), # green jester
    Wizard_Card(59), # blue wizard
  ]
  for trump in range(4):
    assert score_trick(played_cards, trump=trump) == 3


def test_other_tricks():
  """
  test trick scoring in different scenarios where a wizard is played
  - wizard played first
  - wizard played after winning trump card
  - wizard played after another wizard
  - wizard played after jesters
  """
  played_cards: list[Wizard_Card] = [
    Wizard_Card( 1), # red 1
    Wizard_Card(13), # red 13
    Wizard_Card(17), # yellow 2
  ]
  assert score_trick(played_cards, trump=0) == 1
  assert score_trick(played_cards, trump=1) == 2
  assert score_trick(played_cards, trump=2) == 1
  assert score_trick(played_cards, trump=3) == 1
  assert score_trick(played_cards, trump=-1) == 1
  
  played_cards: list[Wizard_Card] = [
    Wizard_Card(12), # red 12
    Wizard_Card(17), # yellow 2
    Wizard_Card( 6), # red 6
    Wizard_Card(13), # red 13
    Wizard_Card(45), # blue jester
    Wizard_Card(40), # green 10
  ]
  assert score_trick(played_cards, trump=0) == 3
  assert score_trick(played_cards, trump=1) == 1
  assert score_trick(played_cards, trump=2) == 5
  assert score_trick(played_cards, trump=3) == 3
  assert score_trick(played_cards, trump=-1) == 3

  played_cards: list[Wizard_Card] = [
    Wizard_Card( 7), # red 7
    Wizard_Card(20), # yellow 5
    Wizard_Card( 6), # red 6
    Wizard_Card(47), # blue 2
    Wizard_Card(11), # red 11
    Wizard_Card(40), # green 10
  ]
  assert score_trick(played_cards, trump=0) == 4
  assert score_trick(played_cards, trump=1) == 1
  assert score_trick(played_cards, trump=2) == 5
  assert score_trick(played_cards, trump=3) == 3
  assert score_trick(played_cards, trump=-1) == 4

  played_cards: list[Wizard_Card] = [
    Wizard_Card( 0), # red jester
    Wizard_Card(15), # yellow jester
    Wizard_Card(30), # green jester
    Wizard_Card(45), # blue jester
  ]
  assert score_trick(played_cards, trump=0) == 0
  assert score_trick(played_cards, trump=1) == 0
  assert score_trick(played_cards, trump=2) == 0
  assert score_trick(played_cards, trump=3) == 0
  assert score_trick(played_cards, trump=-1) == 0
  
  # test round with some jesters and other cards
  played_cards: list[Wizard_Card] = [
    Wizard_Card( 0), # red jester
    Wizard_Card(15), # yellow jester
    Wizard_Card(48), # blue 3
    Wizard_Card(30), # green jester
    Wizard_Card(40), # green 9
  ]
  assert score_trick(played_cards, trump=0) == 2
  assert score_trick(played_cards, trump=1) == 2
  assert score_trick(played_cards, trump=2) == 4
  assert score_trick(played_cards, trump=3) == 2
  assert score_trick(played_cards, trump=-1) == 2
  # print(f"{score_trick(played_cards, trump=0) = }")


def all_tests():
  test_wizard_tricks()
  test_other_tricks()

if __name__ == "__main__":
  all_tests()