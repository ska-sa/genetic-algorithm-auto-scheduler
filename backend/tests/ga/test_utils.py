import pytest
from datetime import date, time, datetime
from ga.utils import lst_to_utc

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
    assert delta <= 5, f"LST to UTC conversion off by {delta:.2f} seconds"