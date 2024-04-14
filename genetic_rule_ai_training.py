"""
This module is responsible for training the genetic rule AI by implementing a genetic algorithm and utiilizing the methods `crossover` and `mutate` of the `Genetic_Wizard_Player` class.

Author: Sebastian Jost
"""
import os

import numpy as np
import matplotlib.pyplot as plt

from program_files.wizard_ais.genetic_rule_ai import Genetic_Wizard_Player
from genetic_algorithm import train_genetic_ai, plot_diversity_measures, load_diversity_values

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
      n_cards_factor = -1,
      remaining_cards_factor = -1,
  )
  child: Genetic_Wizard_Player = player_1.crossover(player_2)
  print(f"{child}")
  child.mutate()
  print(f"{child}")

def init_population(population_size: int) -> list[Genetic_Wizard_Player]:
  """
  Initialize the population for the genetic algorithm using Genetic_Wizard_Player objects with random parameters.
  Players play according to parametrized rules. Those parameters are optimzied by the genetic algorithm.

  inputs:
  -------
      population_size (int): number of players in each generation

  returns:
  --------
      list[Genetic_Wizard_Player]: list of players
  """
  population: list[Genetic_Wizard_Player] = []
  for _ in range(population_size):
    initial_parameters = {
        # trump color choice parameters
        "color_sum_weight": np.random.uniform(-1, 1),
        "color_number_weight": np.random.uniform(-1, 1),
        # trick prediction parameters
        "min_value_for_win": np.random.randint(6, 14),
        "min_trump_value_for_win": np.random.randint(4, 14),
        "round_factor": np.random.uniform(-1, 0),
        "jester_factor": np.random.uniform(-1, 1),
        "prediction_factor": np.random.uniform(0, 1),
        # trick playing parameters
        "trump_value_increase": np.random.uniform(0, 20),
        "wizard_value": np.random.randint(20, 35),
        "n_cards_factor": np.random.uniform(-2, 0),
        "remaining_cards_factor": np.random.uniform(-2, 0),
    }
    population.append(Genetic_Wizard_Player(**initial_parameters))
  return population

def load_genetic_rule_population(path: str) -> list[Genetic_Wizard_Player]:
  """
  Load a population from a pickle file.

  inputs:
  -------
      path (str): path to the pickle file

  returns:
  --------
      list[Genetic_NN_Player]: list of players
  """
  population: list[Genetic_Wizard_Player] = []
  for player_name in os.listdir(path):
    player_path: str = os.path.join(path, player_name)
    player: Genetic_Wizard_Player = Genetic_Wizard_Player.load(player_path)
    population.append(player)
  print(f"Loaded {len(population)} players from {path.strip(os.curdir)}")
  return population


def plot_best_players_avg(best_players_evolution: list[list[tuple[float, Genetic_Wizard_Player]]]) -> None:
  """
  Plot the best players of each generation in four plots:
    - evolution of scores
    - evolution of trump choice parameters
    - evolution of trick prediction parameters
    - evolution of trick playing parameters

  inputs:
  -------
      best_players_evolution (list[list[tuple[float, Genetic_Wizard_Player]]]): list of best players for each generation. Each sublist should contain the same number of pairs (score, player). The player object stores all relevant parameters.
  """
  n_generations = len(best_players_evolution)
  n_players = len(best_players_evolution[0])
  sample_player = best_players_evolution[0][0][1]
  parameters: dict[str, np.ndarray] = {key: np.zeros(n_generations) for key in sample_player.__dict__.keys()}
  parameters["scores"] = np.zeros(n_generations)
  trump_params_to_plot = ["color_sum_weight", "color_number_weight"]
  trick_prediction_params_to_plot = [
    "min_value_for_win",
      "min_trump_value_for_win",
      "round_factor",
      "jester_factor",
      "prediction_factor"
  ]
  trick_playing_params_to_plot = [
      "trump_value_increase",
      "wizard_value",
      "n_cards_factor",
      "remaining_cards_factor"
  ]

  for i, generation in enumerate(best_players_evolution):
    for player_score, player in generation:
      parameters["scores"][i] += player_score
      for key in player.__dict__.keys():
        parameters[key][i] += player.__dict__[key]
    
  for key in parameters.keys():
    parameters[key] /= n_players

  fig, axes = plt.subplots(2, 2, figsize=(10, 10))

  axes[0, 0].plot(parameters["scores"])
  axes[0, 0].set_title('Score Evolution')
  axes[0, 0].set_ylabel('Score')

  for param in trump_params_to_plot:
    axes[0, 1].plot(parameters[param], label=param)
  axes[0, 1].set_title('Trump Choice Parameter Evolution')
  axes[0, 1].set_ylabel('Parameter Value')

  for param in trick_prediction_params_to_plot:
    axes[1, 0].plot(parameters[param], label=param)
  axes[1, 0].set_title('Trick Prediction Parameter Evolution')
  axes[1, 0].set_ylabel('Parameter Value')

  for param in trick_playing_params_to_plot:
    axes[1, 1].plot(parameters[param], label=param)
  axes[1, 1].set_title('Trick Playing Parameter Evolution')
  axes[1, 1].set_ylabel('Parameter Value')

  for x in range(2):
    for y in range(2):
      axes[x, y].set_xlabel('Generation')
      axes[x, y].legend()
      axes[x, y].grid(color="#dddddd")
  plt.show()

def plot_best_players_individual(best_players_evolution: list[list[tuple[float, Genetic_Wizard_Player]]]) -> None:
    """
    Plot the best players of each generation in four separate plots:
      - evolution of scores
      - evolution of trump choice parameters
      - evolution of trick prediction parameters
      - evolution of trick playing parameters

    inputs:
    -------
        best_players_evolution (list[list[tuple[float, Genetic_Wizard_Player]]]): list of best players for each generation. Each sublist should contain the same number of pairs (score, player). The player object stores all relevant parameters.
    """
    # Define the parameters to plot for each player
    trump_params_to_plot = ["color_sum_weight", "color_number_weight"]
    trick_prediction_params_to_plot = [
      "min_value_for_win",
        "min_trump_value_for_win",
        "round_factor",
        "jester_factor",
        "prediction_factor"
    ]
    trick_playing_params_to_plot = [
        "trump_value_increase",
        "wizard_value",
        "n_cards_factor",
        "remaining_cards_factor"
    ]
    # Set up the plot
    fig, axes = plt.subplots(nrows=2, ncols=2)
    # Plot the evolution of the scores
    n_players: int = len(best_players_evolution[0])
    n_generations: int = len(best_players_evolution)
    for player_index in range(n_players):
      # plot score evolution
      scores: list[float] = [0] * n_generations
      for gen_index, generation in enumerate(best_players_evolution):
        scores[gen_index] = generation[player_index][0]
      axes[0, 0].plot(scores, label=f"P{player_index}")
      # plot trump choice parameters evolution
      trump_params: list[list[float]] = [[0] * n_generations for _ in range(len(trump_params_to_plot))]
      for param_index, param_name in enumerate(trump_params_to_plot):
        for gen_index, generation in enumerate(best_players_evolution):
          trump_params[param_index][gen_index] = generation[player_index][1].__dict__[param_name]
        axes[0, 1].plot(trump_params[0], label=f"{param_name} P{player_index}", alpha=0.5)
      # plot trick prediction parameters evolution
      trick_prediction_params: list[list[float]] = [[0] * n_generations for _ in range(len(trick_prediction_params_to_plot))]
      for param_index, param_name in enumerate(trick_prediction_params_to_plot):
        for gen_index, generation in enumerate(best_players_evolution):
          trick_prediction_params[param_index][gen_index] = generation[player_index][1].__dict__[param_name]
        axes[1, 0].plot(trick_prediction_params[0], label=f"{param_name} P{player_index}", alpha=0.5)
      # plot trick playing parameters evolution
      trick_playing_params: list[list[float]] = [[0] * n_generations for _ in range(len(trick_playing_params_to_plot))]
      for param_index, param_name in enumerate(trick_playing_params_to_plot):
        for gen_index, generation in enumerate(best_players_evolution):
          trick_playing_params[param_index][gen_index] = generation[player_index][1].__dict__[param_name]
        axes[1, 1].plot(trick_playing_params[0], label=f"{param_name} P{player_index}", alpha=0.5)
    # add labels and legends
    axes[0, 0].set_title("Evolution of Scores")
    axes[0, 1].set_title("Evolution of Trump Choice Parameters")
    axes[1, 0].set_title("Evolution of Trick Prediction Parameters")
    axes[1, 1].set_title("Evolution of Trick Playing Parameters")
    for x in range(2):
      for y in range(2):
        axes[x, y].set_xlabel("Generation")
        axes[x, y].set_ylabel("Parameter Value")
        axes[x, y].legend()
    axes[0, 0].set_ylabel("Score")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
  import pickle
  np.random.seed(55)
  population_size: int = 500
  population: list[Genetic_Wizard_Player] = init_population(population_size)
  best_parameters, best_player_evolution, pairwise_distances, fitness_variances = train_genetic_ai(
      population=population,
      n_generations=50,
      max_time_s=15*60, # 15 minutes
      n_games_per_generation=300,
      n_repetitions_per_game=50,
      crossover_range=0,
      mutation_rate=0.05,
      mutation_range=0.003,
      track_n_best_players=10,
  )
  print("\nBest parameters:\n  " + "\n  ".join([f"{key} = {value}," for key, value in best_parameters.items()]))

  # with open("best_GenRule_player_evolution.pickle", "wb") as file:
  #   pickle.dump(best_player_evolution, file)
  # print(f"finished saving best_player_evolution.")

  # with open("best_GenRule_player_evolution.pickle", "rb") as file:
  #   best_player_evolution = pickle.load(file)
  plot_best_players_avg(best_player_evolution)
  # plot_best_players_individual(best_player_evolution)
  plot_diversity_measures(pairwise_distances, fitness_variances)