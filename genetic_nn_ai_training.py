"""
This file contains the functions to train neural networks using a genetic algorithm. The neural networks are used to play Wizard. In this file, the architecture of the neural networks is fixed and a genetic algorithm is used to optimize the weights of the neural networks.

Author: Sebastian Jost
"""
import os
import pickle
from tkinter import Tk, filedialog

import matplotlib.pyplot as plt

from program_files.wizard_ais.genetic_nn_ai import Genetic_NN_Player
from genetic_algorithm import train_genetic_ai

def init_population(
    population_size: int,
    trump_color_nn_layers: tuple[int] = (4,),
    prediction_nn_layers: tuple[int] = (5,),
    trick_action_nn_layers: tuple[int] = (5,),
    ) -> list[Genetic_NN_Player]:
  """
  Initialize the population for the genetic algorithm using Genetic_NN_Player objects with random parameters.
  Players play according to parametrized rules. Those parameters are optimzied by the genetic algorithm.

  inputs:
  -------
      population_size (int): number of players in each generation
      trump_color_nn_layers (tuple[int]): number of nodes in each hidden layer of the neural network for the trump color prediction
      prediction_nn_layers (tuple[int]): number of nodes in each hidden layer of the neural network for bidding (predict number of won tricks)
      trick_action_nn_layers (tuple[int]): number of nodes in each hidden layer of the neural network for trick action selection

  returns:
  --------
      list[Genetic_NN_Player]: list of players
  """
  population: list[Genetic_NN_Player] = [Genetic_NN_Player(
    trump_color_nn_layers,
    prediction_nn_layers,
    trick_action_nn_layers) for _ in range(population_size)]
  return population

def load_genetic_nn_population(path: str) -> list[Genetic_NN_Player]:
  """
  Load a population from a pickle file.

  inputs:
  -------
      path (str): path to the pickle file

  returns:
  --------
      list[Genetic_NN_Player]: list of players
  """
  population: list[Genetic_NN_Player] = []
  for player_name in os.listdir(path):
    player_path: str = os.path.join(path, player_name)
    player: Genetic_NN_Player = Genetic_NN_Player.load(player_path)
    population.append(player)
  print(f"Loaded {len(population)} players from {path.strip(os.curdir)}")
  return population

def main(
    population_size: int = 100,
    load_population: bool = False,
    n_generations: int = 50,
    max_time_s: int = 60*30, # 30 minutes
    n_games_per_generation: int = 100,
    n_repetitions_per_game: int = 1,
    crossover_range: float = 0.1,
    mutation_rate: float = 0.1,
    mutation_range: float = 0.1,
    track_n_best_players: int = 5):
  """
  Train a neural network using a genetic algorithm. The neural network is used to play Wizard.

  inputs:
  -------
      population_size (int): number of players in each generation
      n_generations (int): number of generations
      max_time_s (int): maximum time in seconds for the training
      n_games_per_generation (int): number of games per generation
      n_repetitions_per_game (int): number of repetitions per game
      crossover_range (float): range of the random numbers used for crossover
      mutation_rate (float): probability of a mutation
      mutation_range (float): range of the random numbers used for mutation
      track_n_best_players (int): number of best players to track

  returns:
  --------
      best_parameters (list[float]): list of best parameters
      best_player_evolution (list[float]): list of best players
  """
  if not load_population:
    population: list[Genetic_NN_Player] = init_population(population_size)
  else: # open filedialog to choose population folder
    root = Tk()
    root.withdraw()
    path: str = filedialog.askdirectory(
        initialdir=".",
        title="Choose folder of pre-trained population")
    if path:
      population: list[Genetic_NN_Player] = load_genetic_nn_population(path)
    else:
      raise FileNotFoundError("No valid path chosen.")
  # train population
  best_parameters, best_player_evolution = train_genetic_ai(
    population,
    n_generations,
    max_time_s,
    n_games_per_generation,
    n_repetitions_per_game,
    crossover_range,
    mutation_rate,
    mutation_range,
    track_n_best_players)
  with open("best_GenNN_player_evolution.pickle", "wb") as file:
    pickle.dump(best_player_evolution, file)
  return best_parameters, best_player_evolution

def save_best_networks(best_player_evolution: list[list[tuple[float, Genetic_NN_Player]]]):
  """
  Save the best neural networks of the evolution.

  inputs:
  -------
      best_player_evolution (list[Genetic_NN_Player]): list of best players
  """
  best_player: Genetic_NN_Player = best_player_evolution[-1][0][1]
  best_player.save()


def plot_score_evolution(best_player_evolution: list[list[tuple[float, Genetic_NN_Player]]]):
  """
  Plot the score evolution of the best player of each generation.

  inputs:
  -------
      best_player_evolution (list[Genetic_NN_Player]): list of best players
  """
  n_players: int = len(best_player_evolution[0])
  player_scores: list[list[float]] = [[player_score for player_score, _ in generation] for generation in best_player_evolution]
  plt.plot(player_scores, label = [f"Player {player+1}" for player in range(n_players)])
  plt.xlabel("Generation")
  plt.ylabel("Score")
  plt.title(f"Score evolution of the best {n_players} players")
  plt.grid(color="#dddddd")
  plt.show()

if __name__ == "__main__":
  # best_parameters, best_player_evolution = main(
  #     population_size = 50,
  #     n_generations = 300,
  #     n_games_per_generation = 30,
  #     n_repetitions_per_game = 5,
  #     crossover_range = 0.01,
  #     mutation_rate = 0.1,
  #     mutation_range = 0.01,
  #     track_n_best_players = 2
  # )
  # best_parameters, best_player_evolution = main(
  #     population_size = 50,
  #     load_population = False,
  #     n_generations = 1000,
  #     max_time_s = 60*60,
  #     n_games_per_generation = 40,
  #     n_repetitions_per_game = 3,
  #     crossover_range = 0.01,
  #     mutation_rate = 0.1,
  #     mutation_range = 0.01,
  #     track_n_best_players = 3
  # )
  with open("best_GenNN_player_evolution.pickle", "rb") as file:
    best_player_evolution = pickle.load(file)
  for i, generation in enumerate(best_player_evolution):
    if generation == 0:
      best_player_evolution = best_player_evolution[:i]
      with open("best_GenNN_player_evolution.pickle", "wb") as file:
        pickle.dump(best_player_evolution, file)
      break
  # save_best_networks(best_player_evolution)
  plot_score_evolution(best_player_evolution)