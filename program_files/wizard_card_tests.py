import numpy as np
from program_files.wizard_card import Wizard_Card


def print_compare(i, j, deck=tuple(Wizard_Card(i) for i in range(60))):
    res = deck[i] < deck[j]
    print(deck[i], "<", deck[j], "-->", res)
    return res


deck = [Wizard_Card(i) for i in range(60)]

card_pairs = [(0, 1),
              (1, 0),
              (1, 14),
              (0, 14),
              (0, 29),
              (0, 44),
              (0, 59),
              (14, 0),
              (0, 0),
              (0, 15),
              (0, 16),
              (1, 2),
              (8, 14)]

for i, j in card_pairs:
    print_compare(i, j, deck)

np.random.shuffle(deck)
print(sorted(deck))
