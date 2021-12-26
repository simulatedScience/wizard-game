"""
tests for engine
"""
from wizard_card import Wizard_Card
import wizard_engine as engine
from scoring_functions import score_trick
from wizard_functions import get_hands


def test_trick(trick, trump, correct_result):
    print(trick, trump)
    res = score_trick(trick, trump.color)
    print(f"{str(correct_result == res):>5} | score is {res}, should be {correct_result}")
    return correct_result == res

# define and print deck
reds    = [Wizard_Card(i) for i in range( 0, 15)]
yellows = [Wizard_Card(i) for i in range(15, 30)]
greens  = [Wizard_Card(i) for i in range(30, 45)]
blues   = [Wizard_Card(i) for i in range(45, 60)]
print(reds)
print(yellows)
print(greens)
print(blues)

print()

# trick = [Wizard_Card(38), Wizard_Card(6), Wizard_Card(55), Wizard_Card(32)]
# trump = Wizard_Card(27)
# test_trick(trick, trump, 0)

trick = [Wizard_Card(9), Wizard_Card(2), Wizard_Card(57)]
trump = Wizard_Card(50)
test_trick(trick, trump, 2)

# trick = [Wizard_Card(14), Wizard_Card(29), Wizard_Card(3)]
# trump = Wizard_Card(31)
# test_trick(trick, trump, 0)

# trick = [Wizard_Card(0), Wizard_Card(15), Wizard_Card(30)]
# trump = Wizard_Card(52)
# test_trick(trick, trump, 0)

# trick = [Wizard_Card(6), Wizard_Card(55), Wizard_Card(32), Wizard_Card(27), Wizard_Card(21), Wizard_Card(11)]
# trump = Wizard_Card(28)
# test_trick(trick, trump, 3)

# trick = [Wizard_Card(6), Wizard_Card(55), Wizard_Card(32), Wizard_Card(27), Wizard_Card(21), Wizard_Card(11)]
# trump = Wizard_Card(0)
# test_trick(trick, trump, 5)

# trick = [Wizard_Card(6), Wizard_Card(44), Wizard_Card(32), Wizard_Card(27), Wizard_Card(21), Wizard_Card(11)]
# trump = Wizard_Card(28)
# test_trick(trick, trump, 1)

hands, trump = get_hands(3, 19)
print("trump:", trump)
print("trump:", type(trump))
for hand in hands:
    print(hand)