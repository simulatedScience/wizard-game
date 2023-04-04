"""
This module is responsible for training the genetic rule AI by implementing a genetic algorithm and utiilizing the methods `crossover` and `mutate` of the `Genetic_Wizard_Player` class.

Author: Sebastian Jost
"""
import time
import multiprocessing as mp

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
      average_scores_evolution, _ = auto_game.auto_play_multi_threaded(
          n_games = n_repetitions_per_game,
          process_pool = process_pool,
      )
      for i, player_index in enumerate(player_indices):
        individual_scores[player_index].append(average_scores_evolution[-1][i])
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
  new_population: list[Genetic_Wizard_Player] = best_players
  i = 0
  while len(new_population) < len(population):
    # select parents
    parent_1: Genetic_Wizard_Player = best_players[i]
    parent_2: Genetic_Wizard_Player = best_players[np.random.randint(0, len(best_players))]
    # create child
    child: Genetic_Wizard_Player = parent_1.crossover(parent_2, combination_range=crossover_range)
    child.mutate()
    new_population.append(child)
    i = (i + 1) % len(best_players)
  assert len(new_population) == len(population)
  return new_population, sorted_population[:track_n_best_players]


def plot_best_players(best_players_evolution: list[list[tuple[float, Genetic_Wizard_Player]]]):
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
  


if __name__ == "__main__":
  np.random.seed(5)
  best_parameters, best_player_evolution = train_genetic_ai(
      population_size = 30,
      n_generations = 100,
      n_games_per_generation = 30,
      n_repetitions_per_game = 3,
      crossover_range = 0,
  )
  print("\nBest parameters:\n  " + "\n  ".join([f"{key} = {value}," for key, value in best_parameters.items()]))