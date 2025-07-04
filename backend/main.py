import csv
import random
from datetime import date, time, datetime, timedelta
from ga.proposal import Proposal
from ga.utils import parse_time, compute_score, get_global_vars, update_global_vars
from ga.individual import Individual
from ga.timetable import Timetable
from ga.genetic_algorithim import Genetic_Algorithm

START_DATE: date = date.today()
END_DATE: date = date.today()
PROPOSALS: list[Proposal] = []

def can_be_scheduled(proposal: Proposal, start_date: date, end_date: date) -> bool:
    """
    Checks if a proposal can be scheduled within the given start and end dates.

    Args:
        proposal (Proposal): The proposal to be checked for scheduling.
        start_date (date): The start date for the scheduling window.
        end_date (date): The end date for the scheduling window.

    Returns:
        bool: True if the proposal can be scheduled within the given dates, False otherwise.
    """
    for day in range((end_date - start_date).days + 1):
        current_date: date = start_date + timedelta(days=day)
        earliest_start_datetime: datetime = datetime.combine(date=current_date, time=proposal.lst_start_time)
        latest_start_datetime: datetime = datetime.combine(date=current_date, time=proposal.lst_start_end_time)
        for current_datetime in [earliest_start_datetime, latest_start_datetime]:
            if proposal.all_constraints_met(current_datetime):
                return True
    return False

def read_proposals_from_csv(file_path: str) -> list[Proposal]:
    """
    Reads a CSV file containing proposals and returns a list of Proposal objects.

    Args:
        file_path (str): The path to the CSV file containing proposal data.

    Returns:
        list[Proposal]: A list of Proposal objects created from the CSV data.
    """
    proposals = []
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for id, row in enumerate(reader):
                prefered_dates_start_date = []
                prefered_dates_end_date = []
                avoid_dates_start_date = []
                avoid_dates_end_date = []

                # Read preferred dates
                i = 1
                while f'prefered_dates_start_date{i}' in row:
                    prefered_dates_start_date.append(date.fromisoformat(row[f'prefered_dates_start_date{i}']))
                    i += 1

                i = 1
                while f'prefered_dates_end_date{i}' in row:
                    prefered_dates_end_date.append(date.fromisoformat(row[f'prefered_dates_end_date{i}']))
                    i += 1

                # Read avoided dates
                i = 1
                while f'avoid_dates_start_date{i}' in row:
                    avoid_dates_start_date.append(date.fromisoformat(row[f'avoid_dates_start_date{i}']))
                    i += 1

                i = 1
                while f'avoid_dates_end_date{i}' in row:
                    avoid_dates_end_date.append(date.fromisoformat(row[f'avoid_dates_end_date{i}']))
                    i += 1

                # Validate required fields
                if row['minimum_antennas'] == '' or int(row['minimum_antennas']) <= 0:
                    continue  # Invalid data with missing or non-positive 'minimum_antennas'

                if int(row['simulated_duration']) <= 0:
                    continue  # Invalid data with simulated duration less than or equal to 0 sec
                
                proposals.append(Proposal(
                    int(row['id']),
                    row['description'],
                    row['proposal_id'],
                    row['owner_email'],
                    row['instrument_product'],
                    float(row['instrument_integration_time']),
                    row['instrument_band'],
                    row['instrument_pool_resources'],
                    parse_time(row['lst_start']),
                    parse_time(row['lst_start_end']),
                    int(row['simulated_duration']),
                    True if str(row['night_obs']).lower() == "yes" else False,
                    True if str(row['avoid_sunrise_sunset']).lower() == "yes" else False,
                    int(row['minimum_antennas']),
                    row.get('general_comments', ''),
                    prefered_dates_start_date,
                    prefered_dates_end_date,
                    avoid_dates_start_date,
                    avoid_dates_end_date,
                    compute_score(str(row['proposal_id']))
                ))

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return proposals
    

def filter_proposals(proposals: list[Proposal]) -> list[Proposal]:
    """Filter proposals based on the given date range.
    
    Args:
        proposals (list[Proposal]): List of proposals to filter.
    
    Returns:
        list[Proposal]: Filtered list of proposals.
    """
    filtered_proposals: list[Proposal] = list()

    total_timetable_duration: int = (END_DATE - START_DATE).total_seconds()
    cumulative_duration: int = 0

    # Iterate through each proposal and check if it can be scheduled
    for proposal in proposals:
        if not can_be_scheduled(proposal, START_DATE, END_DATE):
            continue
        
        cumulative_duration += proposal.simulated_duration
        if cumulative_duration > total_timetable_duration:
            break
        
        filtered_proposals.append(proposal)  # Add the proposal if it can be scheduled
    
    return filtered_proposals

def main() -> None:
    global START_DATE, END_DATE, PROPOSALS
    START_DATE = date(2024, 1, 1)
    END_DATE = date(2024, 1, 22)
    proposals = read_proposals_from_csv("./proposals/csv/ObsList.csv")
    random.shuffle(proposals)
    filtered_proposals = filter_proposals(proposals)

    PROPOSALS = filtered_proposals
    update_global_vars(START_DATE, END_DATE, [p.to_dict() for p in PROPOSALS])

    # Print number of original and filtered proposals
    print(f"Number of proposals: {len(proposals)}")
    print(f"Number of proposals (Filtered): {len(get_global_vars()[2])}")

    # Generate a random individual
    individual = Individual()
    print(f"Fintess of an Individual (Randomly Generated): {individual.compute_fitness()}")
    
    # Generate the individuals using the genetic algorithm
    genetic_algorithm: Genetic_Algorithm = Genetic_Algorithm(num_of_individuals=10, num_of_generations=500)
    
    # Get the best timetable from the genetic algorithm
    best_timetable: Timetable = Timetable(genetic_algorithm.get_best_fit_individual().schedules)
    
    # Plot the best timetable
    best_timetable.plot()

    # Plot clash free best timetable
    best_timetable.remove_clashes()
    best_timetable.plot(filename_suffix="_clash_free")

if __name__ == "__main__":
    main()