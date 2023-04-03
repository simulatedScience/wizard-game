"""
this module summarized all implemented AI classes and automatically checks which parts of the an AI they implement.
results are stored in global dictionaries. Each dict has some or all names of the implemented AI classes as keys.
  - `ai_classes`: dict - keys are names of each AI class, values are instances of each class.
  for the following three dicts: keys are names of each AI class, values are the corresponding get_action functions
  - `ai_trump_chooser_methods`: dict
  - `ai_bids_chooser_methods`: dict
  - `ai_trick_play_methods`: dict

last edited: 25.05.2022
author: Sebastian Jost
version 0.2
"""
from .uniform_random_ai import Uniform_Random_Ai
from .smart_random_ai import Smart_Random_Ai
from .simple_rule_ai import Simple_Rule_Ai
from .genetic_rule_ai import Genetic_Rule_Ai

# add all implemented AI classes to this list.
#   Everything else is done automatically.
ai_classes = [
    Uniform_Random_Ai,
    Smart_Random_Ai,
    Simple_Rule_Ai
    # Genetic_Rule_Ai
]
ai_classes = {ai_class.name: ai_class() for ai_class in ai_classes}

ai_trump_chooser_methods = dict()
ai_bids_chooser_methods = dict()
ai_trick_play_methods = dict()

for name, ai_class in ai_classes.items():
  if hasattr(ai_class, "get_trump_color_choice"):
    ai_trump_chooser_methods[name] = ai_class.get_trump_color_choice
  if hasattr(ai_class, "get_prediction"):
    ai_bids_chooser_methods[name] = ai_class.get_prediction
  if hasattr(ai_class, "get_trick_action"):
    ai_trick_play_methods[name] = ai_class.get_trick_action
