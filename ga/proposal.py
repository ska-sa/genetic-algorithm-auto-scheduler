from datetime import datetime, date, time

class Proposal():
    """Represents a proposal for a telescope observation"""
    def __init__(self, id: int, description: str, proposal_id: str, owner_email: str, instrument_product: str, instrument_integration_time: float, instrument_band: str, instrument_pool_resources: str, lst_start_time: time, lst_start_end_time: time, simulated_duration: int, night_obs: bool, avoid_sunrise_sunset: bool, minimum_antennas: int, general_comments: str, prefered_dates_start_date: list[date], prefered_dates_end_date: list[date], avoid_dates_start_date: list[date], avoid_dates_end_date: list[date], score: float, scheduled_start_datetime: datetime | None = None) -> None:
        """
        Instantiate a Proposal object with the following attributes: 
        owner's email, observation time and duration, preferred dates, 
        avoided dates, and various other constraints.

        Args:
            id (int): The unique identifier for the proposal.
            description (str): A brief description of the proposal.
            proposal_id (str): The unique identifier for the proposal instance.
            owner_email (str): The email address of the proposal owner.
            instrument_product (str): The instrument product used for the observation.
            instrument_integration_time (float): The integration time for the instrument.
            instrument_band (str): The frequency band of the instrument.
            instrument_pool_resources (str): The resources allocated for the instrument.
            lst_start_time (time): The start time for the last observation.
            lst_start_end_time (time): The end time for the last observation.
            simulated_duration (int): The duration of the simulated observation.
            night_obs (bool): Indicates if the observation is at night.
            avoid_sunrise_sunset (bool): Indicates if sunrise and sunset times should be avoided.
            minimum_antennas (int): The minimum number of antennas required for the observation.
            general_comments (str): Any general comments regarding the proposal.
            prefered_dates_start_date (list[date]): List of preferred start dates for the observation.
            prefered_dates_end_date (list[date]): List of preferred end dates for the observation.
            avoid_dates_start_date (list[date]): List of dates to avoid starting the observation.
            avoid_dates_end_date (list[date]): List of dates to avoid ending the observation.
            score (float): The score assigned to the proposal.
            scheduled_start_datetime (datetime | None): The scheduled start datetime for the observation.

        Returns:
            None
        """
        self.id: int = id
        self.description: str = description
        self.proposal_id: str = proposal_id
        self.owner_email: str = owner_email
        self.instrument_product: str = instrument_product
        self.instrument_integration_time: float = instrument_integration_time
        self.instrument_band: str = instrument_band
        self.instrument_pool_resources: str = instrument_pool_resources
        self.lst_start_time: time = lst_start_time
        self.lst_start_end_time: time = lst_start_end_time
        self.simulated_duration: int = simulated_duration
        self.night_obs: bool = night_obs
        self.avoid_sunrise_sunset: bool = avoid_sunrise_sunset
        self.minimum_antennas: int = minimum_antennas
        self.general_comments: str = general_comments
        self.prefered_dates_start_date: list[date] = prefered_dates_start_date
        self.prefered_dates_end_date: list[date] = prefered_dates_end_date
        self.avoid_dates_start_date: list[date] = avoid_dates_start_date
        self.avoid_dates_end_date: list[date] = avoid_dates_end_date
        self.score: float = score
        self.scheduled_start_datetime: datetime | None = scheduled_start_datetime
