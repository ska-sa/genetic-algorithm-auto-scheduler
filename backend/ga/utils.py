import math
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

ZENITH = 90 + 50 / 60  # Official zenith for sunrise/sunset in degrees

# MATH CONSTANT
TO_RAD = math.pi/180.0

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

def get_sunrise_sunset(at_date: date, latitude: float = SKA_LATITUDE, longitude: float = SKA_LONGITUDE) -> tuple[datetime, datetime]:
    """
    Calculate sunrise and sunset times for a given date, latitude, and longitude.

    Args:
        at_date (date): The date for which to calculate the sunrise and sunset.
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.

    Returns:
        tuple[datetime, datetime]: The sunrise and sunset times as naive datetime objects.
    """

    # 1. Get the day of the year
    N = at_date.timetuple().tm_yday

    # 2. Convert the longitude to hour value and calculate an approximate time
    lng_hour = longitude / 15.0
    t_rise = N + ((6 - lng_hour) / 24)  # For sunrise
    t_set = N + ((18 - lng_hour) / 24)  # For sunset

    # 3a. Calculate the Sun's mean anomaly
    M_rise = (0.9856 * t_rise) - 3.289
    M_set = (0.9856 * t_set) - 3.289

    # 3b. Calculate the Sun's true longitude
    L_rise = M_rise + (1.916 * math.sin(TO_RAD * M_rise)) + (0.020 * math.sin(TO_RAD * 2 * M_rise)) + 282.634
    L_set = M_set + (1.916 * math.sin(TO_RAD * M_set)) + (0.020 * math.sin(TO_RAD * 2 * M_set)) + 282.634

    # Adjust L into the range [0, 360)
    L_rise = force_range(L_rise, 360)
    L_set = force_range(L_set, 360)

    # 4a. Calculate the Sun's declination
    sinDec_rise = 0.39782 * math.sin(TO_RAD * L_rise)
    cosDec_rise = math.cos(math.asin(sinDec_rise))

    sinDec_set = 0.39782 * math.sin(TO_RAD * L_set)
    cosDec_set = math.cos(math.asin(sinDec_set))

    # 4b. Calculate the Sun's local hour angle
    cosH_rise = (math.cos(TO_RAD * ZENITH) - (sinDec_rise * math.sin(TO_RAD * latitude))) / (cosDec_rise * math.cos(TO_RAD * latitude))
    cosH_set = (math.cos(TO_RAD * ZENITH) - (sinDec_set * math.sin(TO_RAD * latitude))) / (cosDec_set * math.cos(TO_RAD * latitude))

    # Check if the sun never rises or sets
    if cosH_rise > 1:
        return None, None  # The sun never rises
    if cosH_set < -1:
        return None, None  # The sun never sets

    # 4c. Finish calculating H and convert into hours
    H_rise = 360 - (1 / TO_RAD) * math.acos(cosH_rise)
    H_set = (1 / TO_RAD) * math.acos(cosH_set)

    H_rise /= 15
    H_set /= 15

    # 5a. Calculate the Sun's right ascension
    RA_rise = (1 / TO_RAD) * math.atan(0.91764 * math.tan(TO_RAD * L_rise))
    RA_set = (1 / TO_RAD) * math.atan(0.91764 * math.tan(TO_RAD * L_set))

    # Adjust RA into the range [0, 360)
    RA_rise = force_range(RA_rise, 360)
    RA_set = force_range(RA_set, 360)

    # 5b. Right ascension value needs to be in the same quadrant as L
    L_quadrant_rise = (math.floor(L_rise / 90)) * 90
    RA_quadrant_rise = (math.floor(RA_rise / 90)) * 90
    RA_rise += (L_quadrant_rise - RA_quadrant_rise)

    L_quadrant_set = (math.floor(L_set / 90)) * 90
    RA_quadrant_set = (math.floor(RA_set / 90)) * 90
    RA_set += (L_quadrant_set - RA_quadrant_set)

    # 5c. Right ascension value needs to be converted into hours
    RA_rise /= 15
    RA_set /= 15

    # 6. Calculate local mean time of rising/setting
    T_rise = H_rise + RA_rise - (0.06571 * t_rise) - 6.622
    T_set = H_set + RA_set - (0.06571 * t_set) - 6.622

    # 7. Adjust back to UTC
    UT_rise = T_rise - lng_hour
    UT_set = T_set - lng_hour

    # 7c. rounding and impose range bounds
    UT_rise = round(UT_rise, 2)
    UT_set = round(UT_set, 2)

    UT_rise = force_range(UT_rise, 24.0)
    UT_set = force_range(UT_set, 24.0)

    # Convert UT to naive datetime objects
    sunrise = datetime.combine(at_date, time(0, 0, 0)) + timedelta(hours=UT_rise)
    sunset = datetime.combine(at_date, time(0, 0, 0)) + timedelta(hours=UT_set)

    return sunrise.replace(second=0, microsecond=0), sunset.replace(second=0, microsecond=0)

def force_range(v, max):
    # Force v to be >= 0 and < max
    if v < 0:
        return v + max
    elif v >= max:
        return v - max
    return v