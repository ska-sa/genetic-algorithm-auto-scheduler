import json
import random
from datetime import datetime, date, time, timedelta

GLOBAL_VARS_FILE = "tmp/global_vars.json"

SECONDS_PER_DAY: int = 86400
SIDEREAL_DAY_SECONDS: int = 86164.0905
J2000: datetime = datetime(2000, 1, 1, 12)  # Reference epoch for JD

# Constants for SKA site
SKA_LATITUDE_STR: str = "-30:42:39.8"
SKA_LONGITUDE_STR: str = "21:26:38.0"

def degrees_string_to_float(degrees: str) -> float:
    """
    Convert a string in the format "hh:mm:ss.s" to a float in degrees.

    Args:
        degrees (str): String in the format "hh:mm:ss.s".

    Returns:
        float: Float representation in degrees.
    """
    sign = -1 if degrees.startswith("-") else 1
    if sign == -1:
        degrees = degrees[1:]
    h, m, s = map(float, degrees.split(":"))
    return sign * (h + m / 60 + s / 3600)

SKA_LATITUDE: float = degrees_string_to_float(SKA_LATITUDE_STR)
SKA_LONGITUDE: float = degrees_string_to_float(SKA_LONGITUDE_STR)

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

def julian_date(date_obj: datetime) -> float:
    """
    Convert a datetime to Julian Date.
    """
    a = (14 - date_obj.month) // 12
    y = date_obj.year + 4800 - a
    m = date_obj.month + 12 * a - 3

    jdn = date_obj.day + ((153 * m + 2) // 5) + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    day_frac = (date_obj.hour - 12) / 24 + date_obj.minute / 1440 + date_obj.second / 86400
    return jdn + day_frac

def gmst_at_0h_utc(jd: float) -> float:
    """
    Compute GMST at 0h UTC in decimal hours.
    """
    d = jd - 2451545.0  # Days since J2000
    gmst = 6.697374558 + 0.06570982441908 * d + 1.00273790935 * 0
    return gmst % 24

def lst_to_utc(date_obj: date, lst_time: time, longitude: float = SKA_LONGITUDE) -> datetime:
    """
    Convert Local Sidereal Time (LST) to UTC datetime (approximate method).

    Args:
        date_obj (date): UTC calendar date.
        lst_time (time): LST as time object.
        longitude (float): Observer longitude in degrees East (default is SKA site).

    Returns:
        datetime: Approximate UTC datetime corresponding to the given LST.
    """
    # 1. Convert LST to decimal hours
    lst_hours: float = lst_time.hour + lst_time.minute / 60 + lst_time.second / 3600

    # 2. Convert observer longitude from degrees to hours
    longitude_hours: float = longitude / 15.0

    # 3. Compute Julian Date at 0h UTC for the given date
    jd_0h: float = julian_date(datetime.combine(date_obj, time(0, 0, 0)))

    # 4. Compute GMST at 0h UTC
    gmst0: float = gmst_at_0h_utc(jd_0h)

    # 5. Calculate Greenwich Sidereal Time (GST) from Local Sidereal Time (LST)
    gst: float = (lst_hours - longitude_hours) % 24

    # 6. Difference between GST and GMST at 0h UTC (in sidereal hours)
    delta_sidereal_hours: float = (gst - gmst0) % 24

    # 7. Convert sidereal time to solar (UTC) time
    SIDEREAL_TO_SOLAR: float = 0.9972695663  # conversion factor
    delta_utc_hours: float = delta_sidereal_hours * SIDEREAL_TO_SOLAR

    # 8. Compute the UTC datetime
    utc_datetime: datetime = datetime.combine(date_obj, time(0, 0, 0)) + timedelta(hours=delta_utc_hours)

    return utc_datetime.replace(microsecond=0)

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