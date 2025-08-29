import pytest
from datetime import datetime, date, time, timedelta
from ga.proposal import Proposal

@pytest.mark.parametrize(
    "proposed_start_datetime, expected_result",
    [
        # Wednesday
        (datetime(2025, 8, 27, 6, 30, 0), True),    # No clash with both arrival and departure
        (datetime(2025, 8, 27, 7, 55, 0), False),   # Clash with arrival time block
        (datetime(2025, 8, 27, 8, 0, 0), False),   # Clash with arrival time block
        (datetime(2025, 8, 27, 9, 0, 0), False),    # Clash with arrival time block
        (datetime(2025, 8, 27, 10, 0, 0), False),   # Clash with arrival time block
        (datetime(2025, 8, 27, 10, 1, 0), True),    # No clash with both arrival and departure
        (datetime(2025, 8, 27, 13, 0, 0), False),    # Clash with depature time block
        (datetime(2025, 8, 27, 14, 11, 0), False),  # Clash with depature time block
        (datetime(2025, 8, 27, 17, 0, 0), True),    # No clash with both arrival and departure

        # Friday
        (datetime(2025, 8, 29, 7, 55, 0), True),    # No clash with both arrival and departure
        (datetime(2025, 8, 29, 14, 11, 0), True),  # No clash with both arrival and departure
        (datetime(2025, 8, 29, 22, 0, 0), True),    # No clash with both arrival and departure

    ]
)
def test_plane_arrival_and_departure_constraint_met(proposed_start_datetime: datetime, expected_result: bool):
    """
    Test the plane arrival and departure constraint checks for various proposed start datetimes.
    """
    proposal = Proposal(
        id=1,
        description="Test Proposal",
        proposal_id="P123",
        owner_email="owner@example.com",
        instrument_product="Instrument A",
        instrument_integration_time=10.0,
        instrument_band="Band 1",
        instrument_pool_resources="Resource A",
        lst_start_time=time(0, 0),
        lst_start_end_time=time(23, 59),
        simulated_duration=3600,  # 1 hour
        night_obs=False,
        avoid_sunrise_sunset=False,
        minimum_antennas=1,
        general_comments="",
    )

    result = proposal.plane_arrival_and_departure_constraint_met(proposed_start_datetime)
    assert result == expected_result, f"Expected {expected_result} but got {result} for proposed start time {proposed_start_datetime}"
