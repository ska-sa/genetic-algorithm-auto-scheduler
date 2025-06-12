import random
from datetime import datetime, date, time, timedelta
from .proposal import Proposal
from .timetable import Timetable
from .utils import read_proposals_from_csv, get_night_window, get_sunrise_sunset, lst_to_utc

class Genetic_Algorithm():
    def __init__(self, start_date: date, end_date: date, proposals: list[Proposal], num_of_timetables: int = 5 * 10, num_of_generations: int = 15 * 1000) -> None:
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.proposals: list[Proposal] = proposals
        self.num_of_timetables: int = num_of_timetables
        self.num_of_generations: int = num_of_generations
        self.timetables: list[Timetable] = list()
        self.generate_timetables()

        for generation in range(num_of_generations):
            self.timetables.sort(key=lambda timetable: timetable.compute_score(), reverse=True)
            self.print_fitness(generation)
            self.evolve()
            
    def generate_timetables(self) -> None:
        for _ in range(self.num_of_timetables):
            self.timetables.append(Timetable(self.start_date, self.end_date, self.proposals))
        return

    def evolve(self, crossover_rate: float = 0.2, mutation_rate: float = 0.1) -> None:
        # Elitism: Keep the best timetables
        self.timetables.sort(key=lambda timetable: timetable.compute_score(), reverse=True)
        elite_timetables: list[Timetable] = self.timetables[:int(self.num_of_timetables * 0.75)]
        
        starting_index: int = self.num_of_timetables - 1 - int(self.num_of_timetables * crossover_rate)
        
        for index in range(starting_index, self.num_of_timetables, 1):
            parent_timetable_1: Timetable = random.choice(elite_timetables)
            parent_timetable_2: Timetable = random.choice(elite_timetables)
            num_offsprings: int = random.randint(4, 8)
            offsprings: list[Timetable] = list()
        
            for _ in range(num_offsprings):
                offspring: Timetable = Timetable(self.start_date, self.end_date, self.proposals, parent_timetable_1.crossover(parent_timetable_2.schedules))
                offspring.mutation(mutation_rate=0.2)
                offsprings.append(offspring)
        
            offsprings.sort(key=lambda timetable: timetable.compute_score(), reverse=True)
            offsprint_timetable: Timetable = random.choice(offsprings[:max(2, int(num_offsprings * 0.4))])
            self.timetables[index] = offsprint_timetable
        return

    def print_fitness(self, generation: int) -> None:
        # Calculate fitness scores for the first up to 5 timetables
        fitness_scores = [timetable.compute_score() for timetable in self.timetables[:min(5, len(self.timetables))]]
        
        # Sort fitness scores in descending order
        sorted_scores = sorted(fitness_scores, reverse=True)

        # Get the first two fittest and the last two least fittest
        fittest_two = sorted_scores[:2]  # First two (fittest)
        least_fittest_two = sorted_scores[-2:]  # Last two (least fittest)

        # Print the results
        print(f"Generation {generation + 1}:\t", end="")
        print(", ".join(f"{score:3.2f}" for score in fittest_two), end=", ..., ")
        print(", ".join(f"{score:3.2f}" for score in least_fittest_two))



    def get_best_fit_timetable(self) -> Timetable:
        # Sort timetables by score and return the best one
        self.timetables.sort(key=lambda timetable: timetable.compute_score(), reverse=True)
        self.timetables[0].remove_clashing_proposals()
        return self.timetables[0]


