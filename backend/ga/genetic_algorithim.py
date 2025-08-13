import random
from .individual import Individual

class Genetic_Algorithm:
    """
    Implements a Genetic Algorithm to optimize the scheduling of a set of proposals.
    """
    def __init__(self, initial_individuals: list[Individual] = list(),num_of_individuals: int = 5 * 10, num_of_generations: int = 15 * 1000) -> None:
        """
        Initializes the GeneticAlgorithm with the given parameters.

        Args:
            initial_individuals (list[Individual]): A list of initial Individuals to start the genetic algorithm.
            num_of_individuals (int, optional): The number of Individuals in the population. Defaults to 5 * 10.
            num_of_generations (int, optional): The number of generations to evolve the population. Defaults to 15 * 1000.

        Returns:
            None
        """
        self.num_of_individuals: int = num_of_individuals
        self.num_of_generations: int = num_of_generations
        self.individuals: list[Individual] = initial_individuals if initial_individuals else list()
        self.generate_individuals()

        for generation in range(num_of_generations):
            self.individuals.sort(key=lambda individual: individual.compute_fitness(), reverse=True)
            self.print_fitness(generation)
            self.evolve()
            
    def generate_individuals(self) -> None:
        """
        Generates the initial population of Individuals for the Genetic Algorithm.

        Args:
            None

        Returns:
            None
        """
        num_of_new_individuals: int = self.num_of_individuals - len(self.individuals)
        for _ in range(min(num_of_new_individuals, self.num_of_individuals)):
            self.individuals.append(Individual())
        return

    def evolve(self, crossover_rate: float = 0.2, mutation_rate: float = 0.1) -> None:
        """
        Evolves the population of Individuals through the genetic algorithm process.

        Args:
            crossover_rate (float, optional): The rate of crossover operation, ranging from 0.0 to 1.0. Defaults to 0.2.
            mutation_rate (float, optional): The rate of mutation operation, ranging from 0.0 to 1.0. Defaults to 0.1.

        Returns:
            None
        """
        # Elitism: Keep the best timetables
        self.individuals.sort(key=lambda individual: individual.compute_fitness(), reverse=True)
        elite_individuals: list[Individual] = self.individuals[:int(self.num_of_individuals * 0.75)]
        
        starting_index: int = self.num_of_individuals - 1 - int(self.num_of_individuals * crossover_rate)
        
        for index in range(starting_index, self.num_of_individuals, 1):
            parent_individual_1: Individual = random.choice(elite_individuals)
            parent_individual_2: Individual = random.choice(elite_individuals)
            num_offsprings: int = random.randint(4, 8)
            offsprings: list[Individual] = list()
        
            for _ in range(num_offsprings):
                offspring: Individual = Individual(parent_individual_1.crossover(parent_individual_2.schedules))
                offspring.mutation(mutation_rate=mutation_rate)
                offsprings.append(offspring)
        
            offsprings.sort(key=lambda individual: individual.compute_fitness(), reverse=True)
            offspring_individual: Individual = random.choice(offsprings[:max(2, int(num_offsprings * 0.4))])
            self.individuals[index] = offspring_individual
        return


    def print_fitness(self, generation: int) -> None:
        """
        Prints the fitness scores of the top and bottom Individuals in the current population.

        Args:
            generation (int): The current generation number.

        Returns:
            None
        """
        # Calculate fitness scores for the first up to 5 timetables
        fitness_scores = [individual.compute_fitness() for individual in self.individuals[:min(5, len(self.individuals))]]
        
        # Sort fitness scores in descending order
        sorted_scores = sorted(fitness_scores, reverse=True)

        # Get the first two fittest and the last two least fittest
        fittest_two = sorted_scores[:2]  # First two (fittest)
        least_fittest_two = sorted_scores[-2:]  # Last two (least fittest)

        # Print the results
        print(f"Generation {generation + 1}:\t", end="")
        print(", ".join(f"{score:3.2f}" for score in fittest_two), end=", ..., ")
        print(", ".join(f"{score:3.2f}" for score in least_fittest_two))
        return

    def get_best_fit_individual(self) -> Individual:
        """
        Retrieves the Individual with the highest fitness score from the current population.

        Args:
            None

        Returns:
            Individual: The Individual with the highest fitness score in the current population.
        """
        # Sort individuals by score and return the best one
        self.individuals.sort(key=lambda individual: individual.compute_fitness(), reverse=True)
        return self.individuals[0]



