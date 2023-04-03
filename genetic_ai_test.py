"""
This module is responsible for training the genetic rule AI by implementing a genetic algorithm and utiilizing the methods `crossover` and `mutate` of the `Genetic_Wizard_Player` class.

Author: Sebastian Jost
"""

from program_files.wizard_ais.genetic_rule_ai import Genetic_Wizard_Player

def test_genetic_methods():
  player_1 = Genetic_Wizard_Player(
      # trump color choice parameters
      color_sum_weight = 0,
      color_number_weight = 1,
      # trick prediction parameters
      min_value_for_win = 11,
      min_trump_value_for_win = 7,
      round_factor = -0.2,
      jester_factor = 0.6,
      prediction_factor = 0.8,
      # trick playing parameters
      trump_value_increase = 14,
      wizard_value = 30,
      n_cards_factor = 0,
      remaining_cards_factor = 0,
  )
  player_2 = Genetic_Wizard_Player(
      # trump color choice parameters
      color_sum_weight = 1,
      color_number_weight = 0,
      # trick prediction parameters
      min_value_for_win = 9,
      min_trump_value_for_win = 6,
      round_factor = -0.15,
      jester_factor = 0.4,
      prediction_factor = 0.9,
      # trick playing parameters
      trump_value_increase = 12,
      wizard_value = 30,
      n_cards_factor = -1
      remaining_cards_factor = -1,
  )
  child: Genetic_Wizard_Player = player_1.crossover(player_2)
  print(f"{child}")
  child.mutate()
  print(f"{child}")

def train_genetic_ai(
    population_size: int = 30,
    n_generations: int = 100,
    n_games_per_generation: int = 100,


if __name__ == "__main__":
  