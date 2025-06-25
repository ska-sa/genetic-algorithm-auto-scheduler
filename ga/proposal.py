from datetime import datetime, date, time, timedelta
from ga.utils import lst_to_utc, get_night_window, get_sunrise_sunset

class Proposal():
    """ A class representing proposals to be scheduled.
    """
    
    def __init__(self, id: int, description: str, proposal_id: str, owner_email: str, instrument_product: str, instrument_integration_time: float, instrument_band: str, instrument_pool_resources: str, lst_start_time: time, lst_start_end_time: time, simulated_duration: int, night_obs: bool, avoid_sunrise_sunset: bool, minimum_antennas: int, general_comments: str, prefered_dates_start_date: list[date], prefered_dates_end_date: list[date], avoid_dates_start_date: list[date], avoid_dates_end_date: list[date], score: float, scheduled_start_datetime: datetime | None = None) -> None:
        
        """ Initializing the Proposal object with its attributes
        
        Each proposal has attribibues that are used to determine when and how it can be scheduled. There are constraints that 
        will be used to filter the peoposals that can be scheduled at a given time.

        Args:
        id (str): Identifier of the proposal
        description (str): A brief description of the proposal.
        proposal_id (str): The unique identifier for the proposal instance.
        owner_email (str): The email address of the proposal owner
        instrument_product (str): The instrument product used for the observation.
        instrument_integration_time (float): The integration time for the instrument.
        instrument_band (str): The frequency band of the instrument.
        instrument_pool_resources (str): The resources allocated for the instrument.
        lst_start_time (time):  The earliest start time of an observation in lst ( Local sidereal time).
        lst_start_end_time (time): The latest start time of an observation in lst ( Local sidereal time).
        simulated_duration (int): The simulated suration of the proposals in seconds.
        night_obs (bool):  The proposal can only be scheduled at night.
        avoid_sunrise_sunset (bool): The proposal should avoid sunrise and sunset times.
        minimum_antennas (int): The minimum required antennas to run the proposal.
        general_comments (str): Any general comments regarding the proposal.
        prefered_dates_start (list[date]): The date that owner prefers the proposal to start by.
        prefered_dates_end (list[date]): The date that owner prefers the proposal to end by.
        avoid_dates_start (list[date]): The start date that owner prefers the proposal to avoid
        avoid_dates_end (list[date]): The end date that owner prefers the proposal to avoid
        score (int): The calculated score to penalize the observation for not adhearing to constraints.
        scheduled_start_datetime (datetime)| None: The actual scheduled start datetime for a proposal.

        Returns:
            None.

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

   #----> Methods to check constraints <----#

    def lst_start_end_time_constraint_met(self, proposed_start_datetime: datetime) -> bool:
        """
        Check if the proposed start time is within the allowed Local Sidereal Time (LST) start and end times.

        Args:
            proposed_start_datetime (datetime): The proposed start datetime for this proposal.

        Returns:
            bool: True if the proposed start time is within the allowed LST range, False otherwise.
        """
        # Convert LST start and end times to UTC for the proposed date
        lst_start_time_utc = lst_to_utc(proposed_start_datetime.date(), self.lst_start_time)
        lst_end_time_utc = lst_to_utc(proposed_start_datetime.date(), self.lst_start_end_time)
        
        # Check if the proposed start datetime is within the allowed LST range
        is_within_lst_range = lst_start_time_utc <= proposed_start_datetime <= lst_end_time_utc
        
        return is_within_lst_range

    def night_obs_constraint_met(self, proposed_start_datetime: datetime) -> bool:
        """
        Check if the proposed start datetime meets the night observation constraints.

        Args:
            proposed_start_datetime (datetime): The proposed start datetime for this proposal.

        Returns:
            bool: True if the night observation constraints are met, False otherwise.
        """
        if self.night_obs:
            # Compute the proposed end datetime based on the simulated duration
            proposed_end_datetime = proposed_start_datetime + timedelta(seconds=self.simulated_duration)
            
            # Get the night window for the proposed date
            night_start_datetime, night_end_datetime = get_night_window(proposed_start_datetime.date())

            # Check if both the start and end datetimes fall within the night window
            is_start_within_night = night_start_datetime <= proposed_start_datetime <= night_end_datetime
            is_end_within_night = night_start_datetime <= proposed_end_datetime <= night_end_datetime
            
            return is_start_within_night and is_end_within_night

        return True  # If night observations are not required, the constraint is considered met

    def avoid_sunrise_sunset_constraint_met(self, proposed_start_datetime: datetime) -> bool:
        """
        Check if the proposed datetime avoids sunrise and sunset constraints.

        Args:
            proposed_start_datetime (datetime): The proposed start datetime for this proposal.

        Returns:
            bool: True if the sunrise and sunset constraints are met, False otherwise.
        """
        if self.avoid_sunrise_sunset:
            # Get sunrise and sunset datetimes for the proposed date
            sunrise_datetime, sunset_datetime = get_sunrise_sunset(date=proposed_start_datetime.date())

            # Compute the end datetime based on the proposal's duration
            proposed_end_datetime = proposed_start_datetime + timedelta(minutes=self.simulated_duration)

            # Check if sunrise or sunset occurs within the proposed start and end datetimes
            is_sunrise_within_proposal = proposed_start_datetime <= sunrise_datetime <= proposed_end_datetime
            is_sunset_within_proposal = proposed_start_datetime <= sunset_datetime <= proposed_end_datetime
            
            # Return True if neither sunrise nor sunset occurs within the proposal's duration
            return not (is_sunrise_within_proposal or is_sunset_within_proposal)

        return True
    
    def all_constraints_met(self, proposed_start_datetime: datetime) -> bool:
        """
        Check if the given proposed_start_datetime satisfies all constraints for this proposal.

        Args:
            proposed_start_datetime (datetime): The proposed start datetime for this proposal.

        Returns:
            bool: True if all constraints are met, False otherwise.
        """
        # Check each constraint and store the results
        is_time_constraint_met = self.lst_start_end_time_constraint_met(proposed_start_datetime)
        is_night_obs_constraint_met = self.night_obs_constraint_met(proposed_start_datetime)
        is_avoid_sunrise_sunset_constraint_met = self.avoid_sunrise_sunset_constraint_met(proposed_start_datetime)
        # Return True only if all constraints are satisfied
        return (is_time_constraint_met and
                is_night_obs_constraint_met and
                is_avoid_sunrise_sunset_constraint_met)
    
    
     
    # def get_proposal_by_id(self, proposal_id: int):
    #   return next((p for p in self.proposals if p.id == proposal_id), None)
