from .uniform_random_ai import Uniform_Random_Ai
from .smart_random_ai import Smart_Random_Ai
from .simple_rule_ai import Simple_Rule_Ai

ai_classes = [
    Uniform_Random_Ai,
    Smart_Random_Ai,
    Simple_Rule_Ai]
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
