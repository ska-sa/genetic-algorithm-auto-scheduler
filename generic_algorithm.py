from copy import deepcopy
import datetime
from math import floor
from pathlib import Path
from individual import Individual, TestIndividual
import matplotlib.pyplot as plt
from typing import List
import random
import numpy as np

from util import evaluate_population_fitnesses, filter_out_impossible_to_place_obs, read_observation_list_file, sunrise_and_sunset_times_to_interval_tree


class GenericAlgorithm():
    def __init__(self, num_of_individuals: int, max_generations: int, heuristics_combination_length: int):
        self.num_of_individuals = num_of_individuals
        self.max_generations = max_generations
        self.heuristics_combination_length = heuristics_combination_length
        self.population: List[Individual] = []
        # TODO: Add-on
        self.mutation_rate = 0.1
        self.reproduction_amount = 0.1
        self.crossover_amount = 0.5
        self.minimize_fitness: bool = False
        self.best_in_every_generation = []

    def gen_population(self) -> None:
        """
        Method to generate a population.

        Returns:
          None
        """
        date = datetime.datetime.strptime('2025-05-01', '%Y-%m-%d')
        day_time_interval_tree, sunrise_sunset_interval_tree = sunrise_and_sunset_times_to_interval_tree(date, 4)

        self.population = [
            Individual(
              heuristics_combination_length=self.heuristics_combination_length,
              day_time_interval_tree=day_time_interval_tree,
              sunrise_sunset_interval_tree=sunrise_sunset_interval_tree,
              antenna_available=64
            )
            for _ in range(self.num_of_individuals)
        ]

    def tournament_selection(self, observation_list, tournament_size=3) -> Individual:
        """
        Method to select individual using tournament selection based on their fitness score.

        Args:
          tournament_size: variable to fine-tune and used in the tournament selection
        
        Returns:
          Individual: an individual object from the selection
        """
        selected_individuals = random.sample(self.population, k=tournament_size)
        best_individual = min(selected_individuals, key=lambda individual: individual.fitness(observation_list))
        return best_individual

    def fetch_crossover(self, individual_parent1: Individual, individual_parent2: Individual) -> List[Individual]:
        """
        Method to perform a crossover between 2 individuals.

        Args:
          individual_parent1: first individual object
          individual_parent2: second individual object
        
        Returns:
          List[Individual]: a list of 2 children after mutation has taken place
        """
        individual_child1, individual_child2 = individual_parent1.crossover(individual_parent2)
        return [individual_child1, individual_child2]

    def show_fitness(self, pop):
        print(len(pop), ":", [i._fitness for i in pop])

    def plot_graph(self, save_path=None):
        ypoints = [i._fitness for i in self.best_in_every_generation]
        xpoints = [i for i in range(1, len(self.best_in_every_generation)+1)]

        plt.title("Best fitness per generation")
        plt.xlabel("Generations")
        plt.ylabel("Best fitness")

        plt.plot(xpoints, ypoints)

        if save_path:
            plt.savefig(save_path)

        plt.show()

    
    def evolve_population(self, observation_list: List[dict]=None) -> Individual:
        """
        Method to run evolution

        Args:
        
        Returns:
          Individual: an individual object
        """
        self.gen_population()
        indiv: Individual = self.population[0]
        possible_to_place_observations, impossible_to_place_observations = filter_out_impossible_to_place_obs(
            observation_list,
            indiv._empty_schedule(),
            indiv._slots_per_day,
            indiv._schedule_slot_duration_s,
            indiv._day_time_interval_tree,
            indiv._sunrise_sunset_interval_tree,
            indiv._antenna_available
        )

        observation_list = possible_to_place_observations

        print("==========INITIAL POP===============")
        self.show_fitness(self.population)
        print("==========================")
        # TODO: if the best individual doesn't improve for X generations, break.
        for generation in range(self.max_generations):
            new_population = []
            num_of_reproduced_indi = floor(self.num_of_individuals * self.reproduction_amount)
            num_of_parents_to_crossover = floor((self.num_of_individuals * self.crossover_amount) / 2)
            num_of_indi_to_mutate = self.num_of_individuals - (num_of_reproduced_indi + num_of_parents_to_crossover*2)

            evaluate_population_fitnesses(self.population, observation_list, self.minimize_fitness)

            for _ in range(int(num_of_reproduced_indi)):
                # Reproduction
                individual_parent = self.tournament_selection(observation_list)
                new_population.append(deepcopy(individual_parent))
                # print("==========REPRO===============")
                # self.show_fitness(new_population)
                # print("==========================")

            for _ in range(int(num_of_parents_to_crossover)):
                individual_parent1 = self.tournament_selection(observation_list)
                individual_parent2 = self.tournament_selection(observation_list)
                individual_offspring = self.fetch_crossover(individual_parent1, individual_parent2)
                new_population.extend(individual_offspring)
                # print("==========X===============")
                # self.show_fitness(new_population)
                # print("==========================")

            for _ in range(int(num_of_indi_to_mutate)):
                individual_parent = self.tournament_selection(observation_list)
                new_population.append(individual_parent.mutate())
                # print("==========MUTATE===============")
                # self.show_fitness(new_population)
                # print("==========================")
            
            evaluate_population_fitnesses(new_population, observation_list, self.minimize_fitness)

            self.population = sorted(new_population, key=lambda individual: individual.fitness(observation_list), reverse=self.minimize_fitness)[:self.num_of_individuals]
            self.best_in_every_generation.append(self.population[0])
            print(f"==========GEN {generation}===============")
            self.show_fitness(self.population)
            print("==========================")
        return self.population[0]