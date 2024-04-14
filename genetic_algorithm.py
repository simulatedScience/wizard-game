import os
import time
import json
import pickle
import multiprocessing as mp
from typing import Any
from tkinter import Tk, filedialog
# from itertools import repeat

import numpy as np
import matplotlib.pyplot as plt
import torch
from memory_profiler import profile

from program_files.wizard_ais.genetic_rule_ai import Genetic_Wizard_Player
from auto_play_genetics import Genetic_Auto_Play


# @profile
def train_genetic_ai(
    population: list[Genetic_Wizard_Player],
    n_generations: int = 100,
    max_time_s: float = 60 * 60, # 1 hour
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
  if n_games_per_generation < len(population) / 3:
    raise ValueError("n_games_per_generation must be at least the population size divided by 3.")
  best_player_evolution: list[list[tuple[float, Genetic_Wizard_Player]]] = [0] * n_generations
  start_time: float = time.time()
  # Initialize lists to store diversity measures
  pairwise_distances: list[float] = [0] * n_generations
  fitness_variances: list[float] = [0] * n_generations
  
  # create process pool for multiprocessing
  print(f"Started training using {mp.cpu_count()} processes.")
  process_pool: mp.Pool = mp.Pool(mp.cpu_count())
  # train population
  for generation in range(n_generations):
    population_scores: list[float] = evaluate_population(
        population,
        n_games_per_generation,
        n_repetitions_per_game,
        process_pool)
    population, best_players = evolve_population(
        population,
        population_scores,
        crossover_range,
        mutation_rate,
        mutation_range,
        track_n_best_players)
    best_player_evolution[generation] = best_players
    # Calculate diversity measures for the current generation
    pairwise_distances[generation] = pairwise_distance(population)
    fitness_variances[generation] = fitness_variance(population_scores)
    # show progress bar for training
    current_time = time.time() - start_time
    print(f"\rTraining AI: {generation + 1}/{n_generations} generations in {current_time: 6.0f} s.", end="")
    print(f" Estimated remaining time: {current_time / (generation + 1) * (n_generations - generation - 1):6.0f} s.", end="")
    print(f" Best score: {max(population_scores):.2f}", end="")
    if current_time > max_time_s:
      print(f"\nStopping training after {generation + 1} generations.  Maximum time of {max_time_s} s exceeded.")
      best_player_evolution = best_player_evolution[:generation + 1]
      pairwise_distances = pairwise_distances[:generation + 1]
      fitness_variances = fitness_variances[:generation + 1]
      break
  # close process pool
  process_pool.close()
  process_pool.join()
  # return best parameters
  print("\nTraining complete.  Evaluating best player...", end="")
  population_scores: list[float] = evaluate_population(population, n_games_per_generation, n_repetitions_per_game)
  best_player: Genetic_Wizard_Player = population[np.argmax(population_scores)]
  print("\b\b\b done.")
  # save last generation
  training_name: str = time.strftime("%Y-%m-%d_%H-%M-%S") + f"_{population[0].__class__.__name__}"
  save_dir: str = os.path.join("genetic_ai_training_history_3", training_name)
  # save_dir: str = os.path.join("genetic_ai_training_history", training_name)
  os.makedirs(save_dir, exist_ok=True)
  for i, player in enumerate(population):
    player.save(save_dir, id=i)
  with open(os.path.join(save_dir, "best_player_evolution.pickle"), "wb") as file:
    pickle.dump(best_player_evolution, file)
  with open(os.path.join(save_dir, "diversity_measures.json"), "w") as file:
    json.dump(
        {"pairwise_distances": pairwise_distances, "fitness_variances": fitness_variances},
        file,
        indent=2
        )
  return best_player.get_parameters(), best_player_evolution, pairwise_distances, fitness_variances

def evaluate_population(
      population: list[Genetic_Wizard_Player],
      n_games_per_generation: int,
      n_repetitions_per_game: int,
      process_pool: mp.Pool = None,
      min_reps_for_multiprocessing: int = 5,
      ) -> list[list[float]]:
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
      list[list[float]: list of scores for each player
  """
  individual_scores: list[list[float]] = [[] for _ in range(len(population))]
  individual_indices: list[int] = list(range(len(population)))

  if process_pool is None and n_repetitions_per_game > min_reps_for_multiprocessing:
    process_pool: mp.Pool = mp.Pool(mp.cpu_count())
  # for n_players in range(3, 7):
  n_players = 3
  player_indices_list = list(individual_indices)
  np.random.shuffle(player_indices_list)
  for _ in range(n_games_per_generation):
    if len(player_indices_list) < n_players:
      additional_indices = list(individual_indices)
      np.random.shuffle(additional_indices)
      player_indices_list.extend(additional_indices)

    player_indices = [player_indices_list.pop(0) for _ in range(n_players)]
    players = [population[i] for i in player_indices]
    auto_game = Genetic_Auto_Play(
        n_players=n_players,
        limit_choices=False,
        max_rounds=20,
        ai_instances=players,
    )
    if n_repetitions_per_game > min_reps_for_multiprocessing:
      scores = auto_game.auto_play_multi_threaded(
          n_games = n_repetitions_per_game,
          process_pool = process_pool,
      )
    else:
      scores: np.ndarray = auto_game.auto_play_single_threaded(
          n_games = n_repetitions_per_game)
    for i, player_index in enumerate(player_indices):
      individual_scores[player_index].append(scores[i])
  # if n_repetitions_per_game > min_reps_for_multiprocessing:
  #   process_pool.close()
  #   process_pool.join()
  # calculate mean score for each player
  for i, player in enumerate(population):
    individual_scores[i] = np.mean(individual_scores[i])
  return individual_scores

def evolve_population(
    population: list[Genetic_Wizard_Player],
    population_scores: list[float],
    survival_rate: float = 0.05,
    crossover_range: float = 0.1,
    mutation_rate: float = 0.1,
    mutation_range: float = 0.1,
    track_n_best_players: int = 5,
    k_tournament: int = 3,
    ) -> tuple[list[Genetic_Wizard_Player], list[tuple[float, Genetic_Wizard_Player]]]:
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
  n_best_players = int(len(population) * survival_rate)
  sorted_population: list[tuple[float, Genetic_Wizard_Player]] = \
      sorted(zip(population_scores, population), reverse=True, key=lambda x: x[0])
  best_players: list[Genetic_Wizard_Player] = [player for _, player in sorted_population][:n_best_players]
  # Create new children
  n_children: int = len(population) - len(best_players)
  new_children: list[Genetic_Wizard_Player] = []
  for _ in range(n_children):
    parent1_idx = tournament_selection(k_tournament, population_scores)
    parent2_idx = tournament_selection(k_tournament, population_scores)
    parent1 = population[parent1_idx]
    parent2 = population[parent2_idx]
    child = _create_child(parent1, parent2, crossover_range, mutation_rate, mutation_range)
    new_children.append(child)

  new_population: list[Genetic_Wizard_Player] = best_players + new_children
  # shuffle new population in-place
  np.random.shuffle(new_population)
  return new_population, sorted_population[:track_n_best_players]
  # # select best players
  # sorted_population: list[tuple[float, Genetic_Rule_Player]] = sorted(zip(population_scores, population), reverse=True, key=lambda x: x[0])
  # best_players: list[Genetic_Rule_Player] = [player for _, player in sorted_population][:len(population)//10]
  # # create new population
  # n_children: int = len(population) - len(best_players)
  # # multi threaded child creation
  # # process_pool: mp.Pool = mp.Pool(mp.cpu_count() * 2)
  # # new_children: list[Genetic_Wizard_Player] = process_pool.starmap(_create_child, repeat((best_players, crossover_range, mutation_rate, mutation_range), n_children))
  # # process_pool.close()
  # # process_pool.join()

def tournament_selection(k: int, individual_scores: list[float]) -> int:
  tournament_indices = np.random.choice(len(individual_scores), size=k, replace=False)
  tournament_scores = [individual_scores[i] for i in tournament_indices]
  winner_index = np.argmax(tournament_scores)
  return tournament_indices[winner_index]

def _create_child(
    parent_1: Genetic_Wizard_Player,
    parent_2: Genetic_Wizard_Player,
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
  # create child
  child: Genetic_Wizard_Player = parent_1.crossover(parent_2, combination_range=crossover_range)
  child.mutate(mutation_rate=mutation_rate, mutation_range=mutation_range)
  return child

# implement measures to characterize the population
def pairwise_distance(population: list[Genetic_Wizard_Player]) -> float:
  """
  Calculate the pairwise distance between all players in the population.
  This is done by sampling 10*len(population) pairs of players and calculating the distance between them

  Args:
      population (list[Genetic_Rule_Player]): list of players

  Returns:
      float: mean pairwise distance between all players in the population
  """
  distances: np.ndarray = np.zeros(len(population) * 10)
  for i in range(len(population) * 10):
    player_1 = np.random.choice(population)
    player_2 = np.random.choice(population)
    player_1_params = flatten_parameters(player_1.get_parameters())
    player_2_params = flatten_parameters(player_2.get_parameters())
    distances[i] = np.linalg.norm(player_1_params - player_2_params)
  return np.mean(distances)

def fitness_variance(population_scores: list[float]) -> float:
  """
  Calculate the variance of the population scores

  Args:
      population_scores (list[float]): list of scores for each player

  Returns:
      float: variance of the population scores
  """
  return np.var(population_scores)

def flatten_parameters(param_dict: dict[str, Any]) -> np.ndarray:
  """
  Flatten the parameters of a player into a 1D array

  Args:
      param_dict (dict[str, Any]): dictionary of parameters. The values can be floats, lists, or torch tensors

  Returns:
      np.ndarray: 1D array of parameters
  """
  flat_list = []
  for key, value in param_dict.items():
    if isinstance(value, float):
      flat_list.append(value)
    elif isinstance(value, list):
      for item in value:
        if isinstance(item, torch.Tensor):
          flat_list.extend(item.flatten().tolist())
        else:
          flat_list.append(item)
    elif isinstance(value, torch.Tensor):
      flat_list.extend(value.flatten().tolist())
  return np.array(flat_list)


def load_diversity_values(file_path: str = None) -> tuple[list[float], list[float]]:
  """
  Load the diversity values from a file that gets requested via a filedialog

  Returns:
      list[float]: list of average pairwise distances of parameters between players
      list[float]: list of average fitness variances of players
  """
  if file_path is None:
    file_path = filedialog.askopenfilename(
        initialdir=".",
        title="Select a diversity history file",
        filetypes=(("json files", "*.json"), ("all files", "*.*")))
  with open(file_path, "r") as file:
    diversity_dict = json.load(file)
  pairwise_distances: list[float] = diversity_dict["pairwise_distances"]
  fitness_variances: list[float] = diversity_dict["fitness_variances"]
  return pairwise_distances, fitness_variances

def load_best_player_evolution(file_path: str = None) -> list[dict[str, Any]]:
  """
  Load the best player evolution from a file that gets requested via a filedialog, unless a filepath is provided

  Args:
      file_path (str, optional): path to the file. Defaults to None.

  Returns:
      bet_player_evolution
  """
  if file_path is None:
    file_path = filedialog.askopenfilename(
        initialdir=".",
        title="Select a best player evolution file",
        filetypes=(("pickle files", "*.pickle"), ("all files", "*.*")))
  with open(file_path, "rb") as file:
    best_player_evolution = pickle.load(file)
  return best_player_evolution



def plot_diversity_measures(
    pairwise_distances: list[float],
    fitness_variances: list[float],
    to_file: bool = False,
    ):
  """
  Plot the pairwise distances and fitness variances over the generations.

  Args:
      pairwise_distances (list[float]): list of pairwise distances
      fitness_variances (list[float]): list of fitness variances
  """
  fig, ax = plt.subplots(2, 1, figsize=(15, 5), sharex=True)
  ax[0].plot(np.arange(len(pairwise_distances)), pairwise_distances, color="#ff8800")
  ax[0].set_title("Pairwise Distance between Players")
  ax[0].set_ylabel("parameter distance")
  ax[1].plot(np.arange(len(fitness_variances)), fitness_variances, color="#ff8800")
  ax[1].set_title("Average fitness variance of population")
  ax[1].set_xlabel("Generation")
  ax[1].set_ylabel("Variance")
  if to_file:
    # create directory if it does not exist
    if not os.path.exists("training_results"):
      os.makedirs("training_results")
    plt.savefig(os.path.join("training_results", "diversity_measures.png"))
  else:
    plt.show()