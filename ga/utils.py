import random
import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, date, time, timedelta
from .proposal import Proposal
import copy

def compute_score(self, proposal_id: str) -> float:
    """
    Calculates the score for the given proposal based on its proposal_id.

    Args:
        proposal_id (str): The unique identifier of the proposal.

    Returns:
        float: The calculated score for the proposal.
    """
    # TODO: Implement the logic for calculating the proposal score
    return float(random.randint(1, 4))

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
                    compute_score(str(row['proposal_id']))  # Assuming get_score is defined elsewhere
                ))

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return proposals

def filter_scheduled_proposals(proposals: list[Proposal], start_date: date, end_date: date) -> list[Proposal]:
    """
    Filter proposals that can be scheduled within the specified date range.

    Args:
        proposals (list[Proposal]): A list of proposals to filter.
        start_date (date): The start date of the scheduling range.
        end_date (date): The end date of the scheduling range.

    Returns:
        list[Proposal]: A list of proposals that can be scheduled within the given date range.
    """
    filtered_proposals: list[Proposal] = []

    total_timetable_duration: int = (end_date - start_date).total_seconds()
    cumulative_duration: int = 0

    # Iterate through each proposal and check if it can be scheduled
    for proposal in proposals:
        if not proposal.can_be_scheduled(start_date, end_date):
            continue
        
        cumulative_duration += proposal.simulated_duration
        if cumulative_duration > total_timetable_duration:
            break
        
        filtered_proposals.append(proposal)  # Add the proposal if it can be scheduled
    
    return filtered_proposals



def get_proposal_by_id(proposals: list[Proposal], proposal_id: int) -> Proposal | None:
    """
    Retrieve a proposal from the list by its unique identifier.

    Args:
        proposals (list[Proposal]): A list of proposals to search through.
        proposal_id (int): The unique identifier of the proposal to retrieve.

    Returns:
        Proposal | None: The proposal with the specified ID if found, otherwise None.
    """
    return next((proposal for proposal in proposals if proposal.id == proposal_id), None)


def lst_to_utc(date: date, lst_time: time) -> datetime:
    """
    Convert Local Sidereal Time (LST) to Coordinated Universal Time (UTC).

    Args:
        date (date): The date for which the LST is provided.
        lst_time (time): The Local Sidereal Time to be converted.

    Returns:
        datetime: The corresponding UTC datetime for the given LST.
    """
    # TODO: Implement conversion from LST to UTC using an appropriate library.
    return datetime.combine(date, lst_time)

def get_night_window(date: date) -> tuple[datetime, datetime]:
    """
    Return the night datetime window for a given day in Cape Town.

    Args:
        date (date): The date for which to calculate the night window.

    Returns:
        tuple[datetime, datetime]: A tuple containing the start and end datetime of the night window.
    """
    # TODO: Consider comuting the night window times using an appropriate library.

    # Start of the night at 18:00 (6 PM)
    start_datetime = datetime(date.year, date.month, date.day, 18, 0, 0)
    
    # End of the night at 06:00 (6 AM) the next day
    end_datetime = start_datetime + timedelta(hours=12)  # 18:00 to 06:00 next day

    return (start_datetime, end_datetime)

def get_sunrise_sunset(date: date) -> tuple[datetime, datetime]:
    """
    Return sunrise and sunset datetime for a given day in Cape Town.

    Args:
        date (date): The date for which to calculate sunrise and sunset.

    Returns:
        tuple[datetime, datetime]: A tuple containing the sunrise and sunset datetime objects.
    """
    # TODO: Consider computing the sunrise and sunset times using an appropriate library for accuracy.

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