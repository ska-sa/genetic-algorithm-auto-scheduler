import random
from datetime import datetime
from .timeslot import Timeslot
from .proposal import Proposal
from .timetable import Timetable

class GeneticAlgorithm():
    def __init__(self, num_of_timetables: int = 5 * 10, num_of_generations: int = 15 * 1000) -> None:
        self.num_of_timetables: int = num_of_timetables
        self.num_of_generations: int = num_of_generations
        self.timetables: list[Timetable] = list()
        self.generate_timetables()

        for generation in range(num_of_generations):
            self.timetables.sort(key=lambda timetable: timetable.score(), reverse=True)
            self.print_fitness(generation)
            self.evolve()
            

    def generate_timetables(self) -> None:
        for _ in range(self.num_of_timetables):
            self.timetables.append(Timetable())
        return

    def evolve(self, crossover_rate: float = 0.2, mutation_rate: float = 0.1) -> None:
        
        # Elitism: Keep the best timetables
        elite_timetables: list[Timetable] = self.timetables[:int(self.num_of_timetables * 0.5)]
        
        # Crossover: Create new timetables by crossing over the best timetables
        new_timetables: list[Timetable] = list()
        for _ in range(int(self.num_of_timetables * (1 - crossover_rate))):
            parent_timetable_1: Timetable = random.choice(elite_timetables)
            parent_timetable_2: Timetable = random.choice(elite_timetables)
            offspring: Timetable = Timetable(parent_timetable_1.crossover(parent_timetable_2.schedules))
            offspring.mutation()
            new_timetables.append(offspring)

        self.timetables.clear()
        # Replace the old population with the new one
        self.timetables = elite_timetables[:int(self.num_of_timetables * crossover_rate)] + new_timetables
        
        return

    def print_fitness(self, generation: int) -> None:
        fitness_scores = [timetable.score() for timetable in self.timetables[:min(5, len(self.timetables))]]
        print(f"Generation {generation + 1}\t\t: ", end="")
        print(" | ".join(f"{score:.2f}\t\t" for score in fitness_scores))

    def get_best_fit_timetable(self) -> Timetable:
        # Sort timetables by score and return the best one
        self.timetables.sort(key=lambda timetable: timetable.score(), reverse=True)
        self.timetables[0].remove_partialy_allocated_proposals()
        return self.timetables[0]
