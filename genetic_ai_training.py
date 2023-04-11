"""
This module is responsible for training the genetic rule AI by implementing a genetic algorithm and utiilizing the methods `crossover` and `mutate` of the `Genetic_Wizard_Player` class.

Author: Sebastian Jost
"""
import time
import multiprocessing as mp
from itertools import repeat

import numpy as np
import matplotlib.pyplot as plt

from program_files.wizard_ais.genetic_rule_ai import Genetic_Wizard_Player
from auto_play_genetics import Genetic_Auto_Play

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

def train_genetic_ai(
    population_size: int = 30,
    n_generations: int = 100,
    n_games_per_generation: int = 100,
    n_repetitions_per_game: int = 30,
    crossover_range: float = 0.1,
    track_n_best_players: int = 5,
    ) -> dict[str, float]:
  """
  Find good parameters for the genetic rule AI by using a genetic algorithm utilizing the methods `crossover` and `mutate` of the `Genetic_Wizard_Player` class.

  inputs:
  -------
      population_size (int): number of players in each generation
      n_generations (int): number of generations to train for
      n_games_per_generation (int): number of games played per generation
      n_repetitions_per_game (int): number of repetitions of each game (keep players the same, shuffle their order)
      crossover_range (float): how far outside the distance between the two parents' values the child's value can be
      track_n_best_players (int): number of best players to track for each generation

  returns:
  --------
      dict[str, float]: dictionary containing the best parameters found
      list[list[tuple[float, Genetic_Wizard_Player]]]: list of the best players of each generation and their average score
  """
  # initialize population
  population: list[Genetic_Wizard_Player] = init_population(population_size)
  best_player_evolution: list[list[tuple[float, Genetic_Wizard_Player]]] = [0]*n_generations
  start_time: float = time.time()
  # train population
  for generation in range(n_generations):
    population_scores: list[float] = evaluate_population(population, n_games_per_generation, n_repetitions_per_game)
    population, best_players = evolve_population(
        population,
        population_scores,
        crossover_range,
        track_n_best_players)
    best_player_evolution[generation] = best_players
    # show progress bar for training
    print(f"\rTraining AI: {generation + 1}/{n_generations} generations.  Estimated remaining time: {(time.time() - start_time) / (generation + 1) * (n_generations - generation - 1):.2f} s.", end="")
  # return best parameters
  population_scores: list[float] = evaluate_population(population, n_games_per_generation, n_repetitions_per_game)
  best_player: Genetic_Wizard_Player = population[np.argmax(population_scores)]
  return best_player.__dict__, best_player_evolution


def init_population(population_size: int) -> list[Genetic_Wizard_Player]:
  """
  Initialize the population for the genetic algorithm.

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


def evaluate_population(
      population: list[Genetic_Wizard_Player],
      n_games_per_generation: int,
      n_repetitions_per_game: int,
      ) -> list[float]:
  """
  Evaluate the population by playing a number of games with each player and calculating their score.
  for `n_games_per_generation` games, first choose a random number of players between 3 and 6 and then choose a random subset of players from the population.
  Those players play `n_repetitions_per_game` games and the score is calculated by averaging the scores of the individual players.

  inputs:
  -------
      population (list[Genetic_Wizard_Player]): list of players
      n_games_per_generation (int): number of games played per generation

  returns:
  --------
      list[float]: list of scores for each player
  """
  individual_scores: list[list[float]] = [[] for _ in range(len(population))]
  individual_indices: list[int] = list(range(len(population)))
  if n_repetitions_per_game > 5:
    process_pool: mp.Pool = mp.Pool(mp.cpu_count() * 2)
  for n_players in range(3, 7):
    for _ in range(n_games_per_generation):
      player_indices: np.ndarray[int] = np.random.choice(individual_indices, size=n_players, replace=False)
      players: list[Genetic_Wizard_Player] = [population[i] for i in player_indices]
      auto_game: Genetic_Auto_Play = Genetic_Auto_Play(
        n_players=n_players,
        limit_choices=False,
        max_rounds=20,
        shuffle_players=True,
        ai_instances=players,
      )
      if n_repetitions_per_game > 5:
        average_scores_evolution, _ = auto_game.auto_play_multi_threaded(
            n_games = n_repetitions_per_game,
            process_pool = process_pool,
        )
      else:
        average_scores_evolution, _ = auto_game.auto_play_single_threaded(n_games = n_repetitions_per_game)
      for i, player_index in enumerate(player_indices):
        individual_scores[player_index].append(average_scores_evolution[-1][i])
  if n_repetitions_per_game > 5:
    process_pool.close()
    process_pool.join()
  for i, player in enumerate(population):
    individual_scores[i] = np.mean(individual_scores[i])
  return individual_scores


def evolve_population(
    population: list[Genetic_Wizard_Player],
    population_scores: list[float],
    crossover_range: float = 0.1,
    track_n_best_players: int = 5,
    ) -> list[Genetic_Wizard_Player]:
  """
  Evolve the population by selecting the best players and using them to create new players.

  inputs:
  -------
      population (list[Genetic_Wizard_Player]): list of players
      population_scores (list[float]): list of scores for each player
      crossover_range (float): how far outside the distance between the two parents' values the child's value can be
      track_n_best_players (int): number of best players to track

  returns:
  --------
      list[Genetic_Wizard_Player]: list of players
  """
  # select best players
  sorted_population: list[tuple[float, Genetic_Wizard_Player]] = sorted(zip(population_scores, population), reverse=True, key=lambda x: x[0])
  best_players: list[Genetic_Wizard_Player] = [player for _, player in sorted_population][:len(population)//2]
  # create new population
  n_children: int = len(population) - len(best_players)
  process_pool: mp.Pool = mp.Pool(mp.cpu_count() * 2)
  new_children: list[Genetic_Wizard_Player] = process_pool.starmap(_create_child, repeat((best_players, crossover_range), n_children))
  new_population: list[Genetic_Wizard_Player] = best_players + new_children
  # shuffle new population in-place
  np.random.shuffle(new_population)
  return new_population, sorted_population[:track_n_best_players]

def _create_child(
    parent_population: list[Genetic_Wizard_Player],
    crossover_range: float,
    ):
  """
  Create a child from two random parents sampled from `parent_population`. Then apply mutations to the newly created child

  Args:
      parent_population (list[Genetic_Wizard_Player]): list of potential parents
      crossover_range (float): how far outside the distance between the two parents' values the child's value can be

  Returns:
      Genetic_Wizard_Player: the child
  """
  parent_1, parent_2 = np.random.choice(parent_population, size=2, replace=False)
  # create child
  child: Genetic_Wizard_Player = parent_1.crossover(parent_2, combination_range=crossover_range)
  child.mutate()
  return child


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
  # np.random.seed(5)
  # best_parameters, best_player_evolution = train_genetic_ai(
  #     population_size = 300,
  #     n_generations = 50,
  #     n_games_per_generation = 400,
  #     n_repetitions_per_game = 5,
  #     crossover_range = 0,
  # )
  # print("\nBest parameters:\n  " + "\n  ".join([f"{key} = {value}," for key, value in best_parameters.items()]))

  # with open("best_player_evolution.pickle", "wb") as file:
  #   pickle.dump(best_player_evolution, file)
  # print(f"finished saving best_player_evolution.")

  with open("best_player_evolution.pickle", "rb") as file:
    best_player_evolution = pickle.load(file)
  plot_best_players_avg(best_player_evolution)
  # plot_best_players_individual(best_player_evolution)