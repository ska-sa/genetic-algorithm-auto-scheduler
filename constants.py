"""Constants used in the RL Scheduler.
"""

def _degrees_string_to_float(degrees: str) -> float:
    """Convert a string in the format "hh:mm:ss.s" to a float in degrees.

    Args:
        degrees (str): String in the format "hh:mm:ss.s".

    Returns:
        float: Float in degrees.
    """
    sign = 1 if degrees[0] != '-' else -1
    if sign == -1:
        degrees = degrees[1:]
    h, m, s = map(float, degrees.split(":"))
    return sign * (h + m / 60 + s / 3600)

SKA_LATITUDE_STR = "-30:42:39.8"
"""Latitude of the SKA site as a string. This is the same value used in OPT.
"""
SKA_LONGITUDE_STR = "21:26:38.0"
"""Longitude of the SKA site as a string. This is the same value used in OPT.
"""

SKA_LATITUDE = _degrees_string_to_float(SKA_LATITUDE_STR)
"""Latitude of the SKA site in degrees. This is the same value used in OPT.
"""

SKA_LONGITUDE = _degrees_string_to_float(SKA_LONGITUDE_STR)
"""Longitude of the SKA site in degrees. This is the same value used in OPT.
"""

MINUTES_IN_SIDEREAL_DAY = 23 * 60 + 56 # 23 hours and 56 minutes (and 4 seconds technically)
"""Number of minutes in a sidereal day. Used for time calculations."""

MINUTES_IN_SOLAR_DAY = 24 * 60 # 24 hours
"""Number of minutes in a solar day. Used for time calculations."""

LST_HOURS_IN_DAY = 23 + 56/60
"""Hours in LST DAY"""

HARD_CONSTRAINT_PENALTY = 1000

if __name__ == "__main__":
    print(f"SKA Latitude: {SKA_LATITUDE} degrees")
    print(f"SKA Longitude: {SKA_LONGITUDE} degrees")
    print(f"Minutes in Sidereal Day: {MINUTES_IN_SIDEREAL_DAY}")
    print(f"Minutes in Solar Day: {MINUTES_IN_SOLAR_DAY}")
    print(f"SKA Latitude String: {SKA_LATITUDE_STR}")
    print(f"SKA Longitude String: {SKA_LONGITUDE_STR}")