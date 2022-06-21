"""
This module starts the wizard game GUI as a new window.

last edited: 25.05.2022
author: Sebastian Jost
version 0.2
"""
# import tkinter as tk
# from program_files.wizard_menu_gui import Wizard_Menu_Gui
from program_files.auto_play_games import Wizard_Auto_Play
from program_files.wizard_ais.simple_rule_ai import Simple_Rule_Ai
from program_files.wizard_ais.smart_random_ai import Smart_Random_Ai
from program_files.wizard_ais.uniform_random_ai import Uniform_Random_Ai

def main():
    # wizard_gui = Wizard_Menu_Gui()
    # tk.mainloop()

  auto_play_class = Wizard_Auto_Play(
    limit_choices=False,
    max_rounds=20,
    shuffle_players=True,
    ai_player_types=[
      # Uniform random AI
      {"trump_choice_var": Uniform_Random_Ai.name,
       "bids_choice_var": Uniform_Random_Ai.name,
       "get_trick_action": Uniform_Random_Ai.name},
      # Smart random AI
      {"trump_choice_var": Smart_Random_Ai.name,
       "bids_choice_var": Smart_Random_Ai.name,
       "get_trick_action": Smart_Random_Ai.name},
      # simple rule AI
      {"trump_choice_var": Simple_Rule_Ai.name,
       "bids_choice_var": Simple_Rule_Ai.name,
       "get_trick_action": Simple_Rule_Ai.name},
      # Smart random AI 2
      {"trump_choice_var": Smart_Random_Ai.name,
       "bids_choice_var": Smart_Random_Ai.name,
       "get_trick_action": Smart_Random_Ai.name},
      # simple rule AI 2
      {"trump_choice_var": Simple_Rule_Ai.name,
       "bids_choice_var": Simple_Rule_Ai.name,
       "get_trick_action": Simple_Rule_Ai.name},
      # Uniform random AI 2
      {"trump_choice_var": Uniform_Random_Ai.name,
       "bids_choice_var": Uniform_Random_Ai.name,
       "get_trick_action": Uniform_Random_Ai.name},
       ],
    n_players=6)
  stats = auto_play_class.auto_play_single_threaded(
    n_games=5000, reset_stats=True)
  print("average scores:\n", stats[0][-5:-1])
  print("win ratios:\n", stats[1][-5:-1])
  auto_play_class.plot_results()

if __name__ == "__main__":
  main()