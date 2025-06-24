import random
import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, date, time, timedelta
import copy

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

