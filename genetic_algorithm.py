import time
import multiprocessing as mp
from itertools import repeat

import numpy as np

from program_files.wizard_ais.genetic_rule_ai import Genetic_Wizard_Player
from auto_play_genetics import Genetic_Auto_Play

def train_genetic_ai(
    population: list[Genetic_Wizard_Player],
    n_generations: int = 100,
    n_games_per_generation: int = 100,
    n_repetitions_per_game: int = 30,
    crossover_range: float = 0.1,
    mutation_rate: float = 0.1,
    mutation_range: float = 0.1,
    track_n_best_players: int = 5,
    ):
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
  best_player_evolution: list[list[tuple[float, Genetic_Wizard_Player]]] = [0] * n_generations
  start_time: float = time.time()
  # train population
  for generation in range(n_generations):
    population_scores: list[float] = evaluate_population(population, n_games_per_generation, n_repetitions_per_game)
    population, best_players = evolve_population(
        population,
        population_scores,
        crossover_range,
        mutation_rate,
        mutation_range,
        track_n_best_players)
    best_player_evolution[generation] = best_players
    # show progress bar for training
    print(f"\rTraining AI: {generation + 1}/{n_generations} generations.  Estimated remaining time: {(time.time() - start_time) / (generation + 1) * (n_generations - generation - 1):.2f} s.", end="")
  # return best parameters
  population_scores: list[float] = evaluate_population(population, n_games_per_generation, n_repetitions_per_game)
  best_player: Genetic_Wizard_Player = population[np.argmax(population_scores)]
  return best_player.get_parameters(), best_player_evolution

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
    mutation_rate: float = 0.1,
    mutation_range: float = 0.1,
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
  # multi threaded child creation
  # process_pool: mp.Pool = mp.Pool(mp.cpu_count() * 2)
  # new_children: list[Genetic_Wizard_Player] = process_pool.starmap(_create_child, repeat((best_players, crossover_range, mutation_rate, mutation_range), n_children))
  # process_pool.close()
  # process_pool.join()
  # single threaded child creation
  new_children: list[Genetic_Wizard_Player] = [_create_child(best_players, crossover_range, mutation_rate, mutation_range) for _ in range(n_children)]
  new_population: list[Genetic_Wizard_Player] = best_players + new_children
  # shuffle new population in-place
  np.random.shuffle(new_population)
  return new_population, sorted_population[:track_n_best_players]

def _create_child(
    parent_population: list[Genetic_Wizard_Player],
    crossover_range: float = 0.1,
    mutation_rate: float = 0.1,
    mutation_range: float = 0.1,
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
  child.mutate(mutation_rate=mutation_rate, mutation_range=mutation_range)
  return child

