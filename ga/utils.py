import random
import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, date, time, timedelta
from .proposal import Proposal
import copy


def read_from_csv(file_path: str) -> list[Proposal]:
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
                prefered_dates_start = []
                prefered_dates_end = []
                avoid_dates_start = []
                avoid_dates_end = []

                # Read preferred dates
                i = 1
                while f'prefered_dates_start_{i}' in row:
                    prefered_dates_start.append(date.fromisoformat(row[f'prefered_dates_start_{i}']))
                    i += 1

                i = 1
                while f'prefered_dates_end_{i}' in row:
                    prefered_dates_end.append(date.fromisoformat(row[f'prefered_dates_end_{i}']))
                    i += 1

                # Read avoided dates
                i = 1
                while f'avoid_dates_start_{i}' in row:
                    avoid_dates_start.append(date.fromisoformat(row[f'avoid_dates_start_{i}']))
                    i += 1

                i = 1
                while f'avoid_dates_end_{i}' in row:
                    avoid_dates_end.append(date.fromisoformat(row[f'avoid_dates_end_{i}']))
                    i += 1

                # Validate required fields
                if row['minimum_antennas'] == '' or int(row['minimum_antennas']) <= 0:
                    continue  # Invalid data with missing or non-positive 'minimum_antennas'

                if int(row['simulated_duration']) < 1800:  # 60 * 30
                    continue  # Invalid data with simulated duration less than 30 minutes

                proposals.append(Proposal(
                    int(row['id']),
                    row['description'],  # Assuming description is added in the Proposal class
                    row['proposal_id'],
                    row['owner_email'],
                    row['instrument_product'],
                    float(row['instrument_integration_time']),
                    row['instrument_band'],
                    row['instrument_pool_resources'],
                    Proposal.parse_time(row['lst_start']),
                    Proposal.parse_time(row['lst_start_end']),
                    int(row['simulated_duration']),
                    True if str(row['night_obs']).lower() == "yes" else False,
                    True if str(row['avoid_sunrise_sunset']).lower() == "yes" else False,
                    int(row['minimum_antennas']),
                    row.get('general_comments', ''),  # Assuming general_comments is added in the Proposal class
                    prefered_dates_start,
                    prefered_dates_end,
                    avoid_dates_start,
                    avoid_dates_end,
                    get_score(str(row['proposal_id']))  # Assuming get_score is defined elsewhere
                ))

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return proposals

def filter_proposals_by_date(proposals: list[Proposal], start_date: date, end_date: date) -> list[Proposal]:
    """
    Filter proposals based on the given date range.
    
    Parameters:
    proposals (list[Proposal]): List of proposals to filter.
    start_date (date): Start date of the range.
    end_date (date): End date of the range.
    
    Returns:
    list[Proposal]: Filtered list of proposals.
    """
    filtered_proposals: list[Proposal] = list()

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

def can_be_scheduled_proposal(proposal: Proposal, start_date: date, end_date: date) -> bool:
    """Check if a proposal can be scheduled based with the start and end dates."""
    for day in range((end_date - start_date).days + 1):  # Include the last day
        # Get the night window for the current day
        night_start_datetime, night_end_datetime = get_night_window(start_date + timedelta(days=day))
        sunrise_datetime, sunset_datetime = get_sunrise_sunset(start_date + timedelta(days=day))

        # Prepare the start times
        min_start_datetime = lst_to_utc(start_date + timedelta(days=day), proposal.lst_start_time)
        max_start_datetime = lst_to_utc(start_date + timedelta(days=day), proposal.lst_start_end_time)

        # Check both start times for night observations
        for start_datetime in [min_start_datetime, max_start_datetime]:
            # Check if scheduling within the night window is possible
            if proposal.night_obs:
                if not (start_datetime >= night_start_datetime and 
                        start_datetime + timedelta(seconds=proposal.simulated_duration) <= night_end_datetime):
                    return False  # Constraint not met

            # Check for sunrise/sunset avoidance
            if proposal.avoid_sunrise_sunset:
                if not (start_datetime + timedelta(seconds=proposal.simulated_duration) <= sunrise_datetime or 
                        start_datetime >= sunset_datetime):
                    return False  # Constraint not met

    return True  # All constraints met


def all_constraints_met(proposal: Proposal, start_datetime: datetime) -> bool:
    """
    Check if all constraints for the proposal are met.
    
    Parameters:
    proposal (Proposal): The proposal to check.
    start_datetime (datetime): The proposed start datetime.
    
    Returns:
    bool: True if all constraints are met, False otherwise.
    """
    return (lst_start_end_time_constraint_met(proposal, start_datetime) and
            night_obs_constraint_met(proposal, start_datetime) and
            avoid_sunrise_sunset_contraint_met(proposal, start_datetime))

def lst_start_end_time_constraint_met(proposal: Proposal, start_datetime: datetime) -> bool:
    """
    Check if the proposal's start time is within the allowed LST start and end time.
    
    Parameters:
    proposal (Proposal): The proposal to check.
    start_datetime (datetime): The proposed start datetime.
    
    Returns:
    bool: True if the constraint is met, False otherwise.
    """
    lst_start_time = lst_to_utc(start_datetime.date(), proposal.lst_start_time) 
    lst_start_end_time = lst_to_utc(start_datetime.date(), proposal.lst_start_end_time)
    return lst_start_time <= start_datetime and start_datetime <= lst_start_end_time

def night_obs_constraint_met(proposal: Proposal, start_datetime: datetime) -> bool:
    if proposal.night_obs:
        # Compute end datetime based on simulated duration
        end_datetime = start_datetime + timedelta(seconds=proposal.simulated_duration)
        night_start_datetime, night_end_datetime = get_night_window(start_datetime.date())

        # Check if both start and end datetimes fall within the night window
        if night_start_datetime <= start_datetime <= night_end_datetime and \
        night_start_datetime <= end_datetime <= night_end_datetime:
            return True  # Constraint met
        return False  # Constraint not met
    return True  # If night observations are not required, constraint is met

def avoid_sunrise_sunset_contraint_met(proposal: Proposal, start_datetime: datetime) -> bool:
    if proposal.avoid_sunrise_sunset:
        # Get sunrise and sunset datetimes
        sunrise_datetime, sunset_datetime = get_sunrise_sunset(date=start_datetime.date())

        # Compute end datetime based on the proposal's duration
        end_datetime = start_datetime + timedelta(minutes=proposal.simulated_duration)

        # Check if sunrise or sunset occurs within the proposal's duration
        if (sunrise_datetime >= end_datetime) or (sunset_datetime <= start_datetime):
            return True  # Constraint met (neither occurs during the proposal)
        return False  # Constraint not met (one of them occurs during the proposal)
    return True  # If avoiding sunrise/sunset is not required, constraint is met


def get_score(proposal_id: str):
    return random.randint(1, 4) # In future we have to classify proposals to get their actual rates


def get_proposal_by_id(proposals: list[Proposal], proposal_id: int) -> Proposal:
    return next((p for p in proposals if p.id == proposal_id), None)


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
    Parse a time string in the format "HH:MM:SS" or "HH:MM" and return a datetime.time object.

    Args:
        time_str (str): A string representing time in "HH:MM:SS" or "HH:MM" format.

    Returns:
        datetime.time: A datetime.time object representing the parsed time.

    Raises:
        ValueError: If the input string is not in the correct format or represents an invalid time.
    """
    try:
        parts = list(map(int, time_str.split(":")))
        
        if len(parts) == 2:  # Format "HH:MM"
            hour, minute = parts
            second = 0  # Default seconds to 0
        elif len(parts) == 3:  # Format "HH:MM:SS"
            hour, minute, second = parts
        else:
            raise ValueError("Time must be in 'HH:MM' or 'HH:MM:SS' format.")

        if hour < 0 or hour > 23:
            raise ValueError("Hour must be between 0 and 23.")
        if minute < 0 or minute > 59:
            raise ValueError("Minute must be between 0 and 59.")
        if second < 0 or second > 59:
            raise ValueError("Second must be between 0 and 59.")

        return time(hour, minute, second)
    except ValueError as e:
        raise ValueError(f"Invalid time format: {time_str}. Error: {e}")