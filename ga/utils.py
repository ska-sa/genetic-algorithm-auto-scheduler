import csv
import random
from datetime import datetime, date, time, timedelta

def compute_score(proposal_id: str) -> float:
    """
    Calculates the score for the given proposal based on its proposal_id.

    Args:
        proposal_id (str): The unique identifier of the proposal.

    Returns:
        float: The calculated score for the proposal.
    """
    # TODO: Implement the logic for calculating the proposal score
    return float(random.randint(1, 4))


def lst_to_utc(date: date, lst_time: time) -> datetime:
    return datetime.combine(date, lst_time)

def get_night_window(date: date) -> tuple[datetime, datetime]:
    """
    Return night datetime window for that day in Cape Town.
    
    Parameters:
    date (date): The date for which to calculate the night window.
    
    Returns:
    tuple[datetime, datetime]: Start and end datetime of the night window.
    """
    # Start of the night at 18:00 (6 PM)
    start_datetime = datetime(date.year, date.month, date.day, 18, 0, 0)
    
    # End of the night at 06:00 (6 AM) the next day
    end_datetime = start_datetime + timedelta(hours=12)  # 18:00 to 06:00 next day

    return (start_datetime, end_datetime)

def get_sunrise_sunset(date: date) -> tuple[datetime, datetime]:
    """
    Return sunrise and sunset datetime for that day in Cape Town.
    
    Parameters:
    date (date): The date for which to calculate sunrise and sunset.
    
    Returns:
    tuple[datetime, datetime]: Sunrise and sunset datetime objects.
    """
    # Set average sunrise and sunset times
    sunrise_datetime = datetime(date.year, date.month, date.day, 6, 0, 0)  # 6:00 AM
    sunset_datetime = datetime(date.year, date.month, date.day, 18, 0, 0)  # 6:00 PM
    return sunrise_datetime, sunset_datetime


def parse_time(time_str: str) -> time:
    """
    Parse a time string in the format "HH:MM" and return a datetime.time object.
    """
    hour, minute = map(int, time_str.split(":"))
    return time(hour, minute)

def can_be_scheduled_proposal(proposal: "Proposal", start_date: date, end_date: date) -> bool:
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
   
def read_proposals_from_csv(file_path: str) -> list["Proposal"]:
    """
    Reads a CSV file containing proposals and returns a list of Proposal objects.

    Args:
        file_path (str): The path to the CSV file containing proposal data.

    Returns:
        list[Proposal]: A list of Proposal objects created from the CSV data.
    """
    proposals = []
    from .proposal import Proposal
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
    

def filter_proposals_by_date(proposals: list["Proposal"],start_date: date, end_date: date) -> list["Proposal"]:
    """Filter proposals based on the given date range.
    
    Args:
        proposals (list[Proposal]): List of proposals to filter.
        start_date (date): Start date of the range.
        end_date (date): End date of the range.
    
    Returns:
        list[Proposal]: Filtered list of proposals.
    """
    filtered_proposals: list["Proposal"] = list()

    total_timetable_duration: int = (end_date - start_date).total_seconds()
    cumulative_timetable_duration: int = 0

    # Iterate through each proposal and check if it can be scheduled
    for proposal in proposals:

        if not can_be_scheduled_proposal(proposal, start_date, end_date):  # Check if the proposal can be scheduled
            continue
        
        cumulative_timetable_duration += proposal.simulated_duration
        if cumulative_timetable_duration > total_timetable_duration * 0.85:
            break
        
        filtered_proposals.append(proposal) # Add the proposal if it can be scheduled
    return filtered_proposals
    
