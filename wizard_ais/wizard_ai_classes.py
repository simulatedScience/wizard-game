from .uniform_random_ai import Uniform_Random_Ai

ai_classes = {
    # "uniform_random_ai": Uniform_Random_Ai,
    Uniform_Random_Ai.name: Uniform_Random_Ai
}

ai_trump_chooser_classes = dict()
ai_bids_chooser_classes = dict()
ai_trick_play_classes = dict()

for name, ai_class in ai_classes.items():
  if hasattr(ai_class, "get_trump_color_choice"):
    ai_trump_chooser_classes[name] = ai_class.get_trump_color_choice
  if hasattr(ai_class, "get_prediction"):
    ai_bids_chooser_classes[name] = ai_class.get_prediction
  if hasattr(ai_class, "get_trick_action"):
    ai_trick_play_classes[name] = ai_class.get_trick_action
