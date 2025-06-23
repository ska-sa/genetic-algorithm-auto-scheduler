import random
from datetime import date
from ga.proposal import Proposal
# from .timetable import Timetable
# from .genetic_algorithim import Genetic_Algorithm
# from .utils import read_proposals_from_csv, filter_proposals_by_date

def main():
    # start_date: date = date(2024, 1, 1)
    # end_date: date = date(2024, 1, 22)

    proposals: list[Proposal] = Proposal.read_proposals_from_csv("./proposals/csv/ObsList.csv")
    print(f"Number of proposals: {len(proposals)}")
        # random.shuffle(proposals)
    # filtered_proposals: list[Proposal] = filter_proposals_by_date(proposals, start_date, end_date)

    # #breakpoint()

    # # Generate the timetable using the genetic algorithm
    # genetic_algorithm: Genetic_Algorithm = Genetic_Algorithm(start_date=start_date, end_date=end_date, proposals=filtered_proposals, num_of_timetables=10, num_of_generations=500)
    # # Get the best timetable from the genetic algorithm
    # best_timetable: Timetable = genetic_algorithm.get_best_fit_timetable()
    # # Print the best timetable
    # best_timetable.plot()
    
if __name__ == "__main__":
    main()