import json
import random
from datetime import datetime, date, time, timedelta

GLOBAL_VARS_FILE = "tmp/global_vars.json"

def get_global_vars() -> tuple[date, date, list[dict]]:
    """
    Get the current values of the global variables from the JSON file.

    Args:
        None

    Returns:
        tuple[date, date, list[dict]]: The current values of START_DATE, END_DATE, and PROPOSALS.
    """
    try:
        with open(GLOBAL_VARS_FILE, "r") as file:
            data = json.load(file)
            start_date = date.fromisoformat(data["START_DATE"])
            end_date = date.fromisoformat(data["END_DATE"])
            proposals = data["PROPOSALS"]
            return start_date, end_date, proposals
    except FileNotFoundError:
        return date(2024, 1, 1), date(2024, 1, 22), []

def update_global_vars(start_date: date = date.today(), end_date: date = date.today(),proposals: list[dict] = []) -> None:
    """
    Update the global variables and write them to the JSON file.

    Args:
        start_date (date): The new start date.
        end_date (date): The new end date.
        proposals (list[dict]): The new list of proposal data.

    Returns:
        None
    """
    data = {
        "START_DATE": start_date.isoformat(),
        "END_DATE": end_date.isoformat(),
        "PROPOSALS": proposals
    }
    with open(GLOBAL_VARS_FILE, "w") as file:
        json.dump(data, file)

def parse_time(time_str: str) -> time:
    """
    Parses a time string in the format "HH:MM" and returns a datetime.time object.

    Args:
        time_str (str): A time string in the format "HH:MM".

    Returns:
        time: A datetime.time object representing the parsed time.
    """
    hour, minute = map(int, time_str.split(":"))
    return time(hour, minute)

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
    """
    Converts a Local Sidereal Time (LST) time to a UTC datetime.

    Args:
        date (date): The date for which the LST time is given.
        lst_time (time): The LST time to be converted to UTC.

    Returns:
        datetime: The UTC datetime corresponding to the given LST time and date.
    """
    return datetime.combine(date, lst_time)

def get_night_window(date: date) -> tuple[datetime, datetime]:
    """
    Returns the night datetime window for the given date in Cape Town.

    Args:
        date (date): The date for which to calculate the night window.

    Returns:
        tuple[datetime, datetime]: The start and end datetime of the night window.
    """
    # Start of the night at 18:00 (6 PM)
    start_datetime = datetime(date.year, date.month, date.day, 18, 0, 0)

    # End of the night at 06:00 (6 AM) the next day
    end_datetime = start_datetime + timedelta(hours=12)  # 18:00 to 06:00 next day

    return (start_datetime, end_datetime)

def get_sunrise_sunset(date: date) -> tuple[datetime, datetime]:
    """
    Returns the sunrise and sunset datetime for the given date in Cape Town.

    Args:
        date (date): The date for which to calculate the sunrise and sunset.

    Returns:
        tuple[datetime, datetime]: The sunrise and sunset datetime objects.
    """
    # Set average sunrise and sunset times
    sunrise_datetime = datetime(date.year, date.month, date.day, 6, 0, 0)  # 6:00 AM
    sunset_datetime = datetime(date.year, date.month, date.day, 18, 0, 0)  # 6:00 PM
    return sunrise_datetime, sunset_datetime