import random
from datetime import date
from .proposal import Proposal
from .timetable import Timetable
from .individual import Individual
from .genetic_algorithim import GeneticAlgorithm
from .utils import read_proposals_from_csv, filter_scheduled_proposals

def main():
    start_date: date = date(2024, 1, 1)
    end_date: date = date(2024, 1, 22)
    proposals: list[Proposal] = read_proposals_from_csv('./proposals/csv/ObsList.csv')
    random.shuffle(proposals)
    filtered_proposals: list[Proposal] = filter_scheduled_proposals(proposals, start_date, end_date)

    #breakpoint()

    # Generate the timetable using the genetic algorithm
    genetic_algorithm: GeneticAlgorithm = GeneticAlgorithm(start_date=start_date, end_date=end_date, proposals=filtered_proposals, num_of_individuals=10, num_of_generations=500)
    
    # Get the best individual
    best_individual: Individual = genetic_algorithm.get_best_fit_individual()
    
    # Get the best timetable from the genetic algorithm
    #best_timetable: Timetable = genetic_algorithm.get_best_fit_timetable()
    # Print the best timetable
    #best_timetable.plot()
    
if __name__ == "__main__":
    main()