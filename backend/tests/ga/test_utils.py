import pytest
from datetime import date, time, datetime, timezone, timedelta
from ga.utils import lst_to_utc, get_sunrise_sunset, get_plane_arrival_and_departure_blocks

SARAO_CPT_LAT: float = -33.94470
SARAO_CPT_LON: float = 18.47810

@pytest.mark.parametrize(
    "test_date, test_lst, expected_utc",
    [
        (
            date(2025, 8, 20),
            time(9, 25, 7),
            datetime.combine(date(2025, 8, 20), time(10, 3, 20)),
        ),
        (
            date(2024, 10, 14),
            time(11, 11, 43),
            datetime.combine(date(2024, 10, 14), time(8, 12, 27)),
        ),
        (
            date(2025, 8, 20),
            time(12, 38, 55),
            datetime.combine(date(2025, 8, 20), time(13, 16, 37))
        )
    ]
)
def test_lst_to_utc_matches_expected(test_date: date, test_lst: time, expected_utc: datetime):
    """
    Parametrized test for LST -> UTC conversion using SKA site default longitude.
    Validates that the result is a datetime and within +/- 5 second of expected.
    """
    result: datetime = lst_to_utc(test_date, test_lst)

    assert isinstance(result, datetime)

    # Allow for 5-second tolerance
    delta = abs((result - expected_utc).total_seconds())

    print(f"\nCalculated UTC: {result} | Expected UTC: {expected_utc} | Δ = {delta:.2f} seconds")

    assert delta <= 5, f"LST to UTC conversion off by {delta:.2f} seconds"

@pytest.mark.parametrize(
    "test_date, test_lst, wrong_expected_utc",
    [
        (
            date(2025, 8, 20),
            time(9, 25, 7),
            datetime.combine(date(2024, 11, 20), time(12, 0, 0)),
        ),
        (
            date(2024, 10, 14),
            time(11, 11, 43),
            datetime.combine(date(2024, 10, 14), time(7, 55, 0)),
        ),
    ]
)
def test_lst_to_utc_does_not_match_wrong_utc(test_date: date, test_lst: time, wrong_expected_utc: datetime):
    """
    This test ensures the LST → UTC conversion does NOT match incorrect reference values.
    """
    result: datetime = lst_to_utc(test_date, test_lst)

    delta: float = abs((result - wrong_expected_utc).total_seconds())
    
    print(f"\nCalculated UTC: {result} | Expected (wrong) UTC: {wrong_expected_utc} | Δ = {delta:.2f} seconds")

    assert delta > 5, f"Test failed: LST conversion too close to wrong value ({delta:.2f} seconds)"

@pytest.mark.parametrize(
    "test_date, expected_sunrise, expected_sunset",
    [
        (
            date(2025, 6, 21), # Winter
            datetime(2025, 6, 21, 7, 31, 0),
            datetime(2025, 6, 21, 17, 41, 0),
        ),
        (
            date(2025, 12, 21), # Summer
            datetime(2025, 12, 21, 5, 27, 0),
            datetime(2025, 12, 21, 19, 36, 0),
        ),
        (
            date(2025, 3, 20), # Autumn
            datetime(2025, 3, 20, 6, 37, 0),
            datetime(2025, 3, 20, 18, 45, 0),
        ),
        (
            date(2025, 8, 26), # Spring
            datetime(2025, 8, 26, 6, 56, 0),
            datetime(2025, 8, 26, 18, 15, 0),
        ),
    ]
)
def test_get_sunrise_sunset(test_date: date, expected_sunrise: datetime, expected_sunset: datetime):
    """
    Parametrized test for sunrise and sunset times.
    Validates that the calculated times are within +/- 60 seconds of the expected values.
    """
    sunrise, sunset = get_sunrise_sunset(test_date)

    # Converting sunset and sunrise to local time
    sunrise += timedelta(hours=2)
    sunset += timedelta(hours=2)

    assert isinstance(sunrise, datetime)
    assert isinstance(sunset, datetime)

    # Allow for 60-seconds tolerance
    sunrise_delta = abs((sunrise - expected_sunrise).total_seconds())
    sunset_delta = abs((sunset - expected_sunset).total_seconds())

    print(f"\nCalculated Sunrise: {sunrise} | Expected Sunrise: {expected_sunrise} | Δ = {sunrise_delta:.2f} seconds")
    print(f"Calculated Sunset: {sunset} | Expected Sunset: {expected_sunset} | Δ = {sunset_delta:.2f} seconds")

    assert sunrise_delta <= 60, f"Sunrise calculation off by {sunrise_delta:.2f} seconds"
    assert sunset_delta <= 60, f"Sunset calculation off by {sunset_delta:.2f} seconds"

@pytest.mark.parametrize(
    "test_date, expected_sunrise, expected_sunset",
    [
        (
            date(2025, 8, 26),
            datetime(2025, 8, 26, 7, 11, 0),
            datetime(2025, 8, 26, 18, 24, 0)
        )
    ]
)
def test_get_sunrise_sunset_cpt(test_date: date, expected_sunrise: datetime, expected_sunset: datetime):
    """
    Parametrized test for sunrise and sunset times.
    Validates that the calculated times are within +/- 60 seconds of the expected values.
    """
    sunrise, sunset = get_sunrise_sunset(test_date, latitude=SARAO_CPT_LAT, longitude=SARAO_CPT_LON)

    # Converting sunset and sunrise to local time
    sunrise += timedelta(hours=2)
    sunset += timedelta(hours=2)

    assert isinstance(sunrise, datetime)
    assert isinstance(sunset, datetime)

    # Allow for 60-seconds tolerance
    sunrise_delta = abs((sunrise - expected_sunrise).total_seconds())
    sunset_delta = abs((sunset - expected_sunset).total_seconds())

    print(f"\nCalculated Sunrise: {sunrise} | Expected Sunrise: {expected_sunrise} | Δ = {sunrise_delta:.2f} seconds")
    print(f"Calculated Sunset: {sunset} | Expected Sunset: {expected_sunset} | Δ = {sunset_delta:.2f} seconds")

    assert sunrise_delta <= 60, f"Sunrise calculation off by {sunrise_delta:.2f} seconds"
    assert sunset_delta <= 60, f"Sunset calculation off by {sunset_delta:.2f} seconds"

@pytest.mark.parametrize(
    "test_date, wrong_expected_sunrise, wrong_expected_sunset",
    [
        (
            date(2025, 6, 21),
            datetime(2025, 6, 21, 7, 0, 0),
            datetime(2025, 6, 21, 19, 0, 0),
        ),
        (
            date(2025, 12, 21),
            datetime(2025, 12, 21, 7, 0, 0),
            datetime(2025, 12, 21, 18, 0, 0),
        ),
    ]
)
def test_get_sunrise_sunset_does_not_match_wrong_values(test_date: date, wrong_expected_sunrise: datetime, wrong_expected_sunset: datetime):
    """
    This test ensures the sunrise/sunset calculations do NOT match incorrect reference values.
    """
    sunrise, sunset = get_sunrise_sunset(test_date)

    # Converting sunset and sunrise to local time
    sunrise += timedelta(hours=2)
    sunset += timedelta(hours=2)

    sunrise_delta = abs((sunrise - wrong_expected_sunrise).total_seconds())
    sunset_delta = abs((sunset - wrong_expected_sunset).total_seconds())

    print(f"\nCalculated Sunrise: {sunrise} | Wrong Expected Sunrise: {wrong_expected_sunrise} | Δ = {sunrise_delta:.2f} seconds")
    print(f"Calculated Sunset: {sunset} | Wrong Expected Sunset: {wrong_expected_sunset} | Δ = {sunset_delta:.2f} seconds")

    assert sunrise_delta > 60, f"Sunrise calculation too close to wrong value ({sunrise_delta:.2f} seconds)"
    assert sunset_delta > 60, f"Sunset calculation too close to wrong value ({sunset_delta:.2f} seconds)"

@pytest.mark.parametrize(
    "test_date, expected_blocks",
    [
        (date(2025, 4, 30), [       # Wednesday (a long time ago)
            (datetime(2025, 4, 30, 8, 0, 0), datetime(2025, 4, 30, 10, 0, 0)),  # Arrival
            (datetime(2025, 4, 30, 14, 0, 0), datetime(2025, 4, 30, 16, 30, 0)),  # Departure
        ]),
        (date(2025, 8, 24), []),    # Sunday
        (date(2025, 8, 25), []),    # Monday
        (date(2025, 8, 26), []),    # Tuesday
        (date(2025, 8, 27), [       # Wednesday
            (datetime(2025, 8, 27, 8, 0, 0), datetime(2025, 8, 27, 10, 0, 0)),  # Arrival
            (datetime(2025, 8, 27, 14, 0, 0), datetime(2025, 8, 27, 16, 30, 0)),  # Departure
        ]),
        (date(2025, 8, 28), []),    # Thursday
        (date(2025, 8, 29), []),    # Friday
        (date(2025, 8, 30), [])     # Saturday 
    ]
)
def test_get_plane_arrival_and_departure_blocks(test_date: date, expected_blocks: list[tuple[datetime, datetime]]):
    """
    Test the plane arrival and departure blocks for various dates.
    """

    plane_blocks: list[tuple[datetime, datetime]] = get_plane_arrival_and_departure_blocks(test_date)
    assert plane_blocks == expected_blocks, f"Expected {expected_blocks}, but got {plane_blocks}"
