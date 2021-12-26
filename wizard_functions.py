import numpy as np
from typing import Tuple

from wizard_card import Wizard_Card

def get_hands(n_players: int, round_nbr: int) -> Tuple[list, Wizard_Card]:
    """
    return a list of lists, where each sublist represents one player's cards.
    also returns the trump card
    each card is represented by an integer k:
        - k//15 is in [0,1,2,3] representing the colors.
        - k%15 represents the card type: [J, 1,2,...,13, W]
         0 - 14: red
        15 - 29: yellow
        30 - 44: green
        45 - 59: blue

    inputs:
    -------
        n_players (int) - number of players playing
        round_nbr (int) - current round number = number of cards each player gets this round
    """
    deck = [Wizard_Card(i) for i in range(60)]
    np.random.shuffle(deck)
    hands = [[]]*n_players
    for i in range(n_players):
        hands[i] = deck[i*round_nbr:i*round_nbr+round_nbr]
    # determine trump for the round
    if n_players*round_nbr == 60:
        trump_card = None
    else:
        trump_card = deck[n_players*round_nbr]
    return hands, trump_card