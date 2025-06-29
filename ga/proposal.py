from datetime import datetime, date, time, timedelta
import csv
import random
from ga.utils import lst_to_utc, get_night_window, get_sunrise_sunset, parse_time, get_score

class Proposal():
    """ A class representing proposals to be scheduled.
    """
    
    def __init__(self, id: int, owner_email: str, build_time: int,
                 prefered_dates_start: list[date], prefered_dates_end: list[date],
                 avoid_dates_start: list[date], avoid_dates_end: list[date],
                 night_obs: bool, avoid_sunrise_sunset: bool, minimum_antennas: int,
                 lst_start_time: time = time(0, 0), lst_start_end_time: time = time(23, 59),
                 simulated_duration: int = 60 * 60, score: int = 1,
                 scheduled_start_datetime: datetime | None = None):
        
        """ Initializing the Proposal object with its attributes
        
        Each proposal has attribibues that are used to determine when and how it can be scheduled. There are constraints that 
        will be used to filter the peoposals that can be scheduled at a given time.

        Args:
        id (str): Identifier of the proposal
        owner_email (str): The email address of the proposal owner
        build_time (int):  The time it tasks to build a subarray in preparation for a proposal.
        prefered_dates_start (list[date]): The date that owner prefers the proposal to start by.
        prefered_dates_end (list[date]): The date that owner prefers the proposal to end by.
        avoid_dates_start (list[date]): The start date that owner prefers the proposal to avoid
        avoid_dates_end (list[date]): The end date that owner prefers the proposal to avoid
        night_obs (bool):  The proposal can only be scheduled at night.
        avoid_sunrise_sunset (bool): The proposal should avoid sunrise and sunset times.
        minimum_antennas (int): The minimum required antennas to run the proposal.
        lst_start_time (time):  The earliest start time of an observation in lst ( Local sidereal time).
        lst_start_end_time (time): The latest start time of an observation in lst ( Local sidereal time).
        simulated_duration (int): The simulated suration of the proposals in seconds.
        score (int): The calculated score to penalize the observation for not adhearing to constraints.
        scheduled_start_datetime (datetime)| None: The actual scheduled start datetime for a proposal.

        Returns:
            list[proposal]: A list of proposals with their attributes set.

        """
        self.id: int = id
        self.owner_email: str = owner_email
        self.build_time: int = build_time
        self.prefered_dates_start: list[date] = prefered_dates_start
        self.prefered_dates_end: list[date] = prefered_dates_end
        self.avoid_dates_start: list[date] = avoid_dates_start
        self.avoid_dates_end: list[date] = avoid_dates_end
        self.night_obs: bool = night_obs
        self.avoid_sunrise_sunset: bool = avoid_sunrise_sunset
        self.minimum_antennas: int = minimum_antennas
        self.lst_start_time: time = lst_start_time
        self.lst_start_end_time: time = lst_start_end_time
        self.simulated_duration: int = simulated_duration
        self.score: int = score
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

    def avoid_sunriset_sunset_constraint_met(self, proposed_start_datetime: datetime) -> bool:
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
        is_avoid_sunrise_sunset_constraint_met = self.avoid_sunrise_sunset_contraint_met(proposed_start_datetime)

        # Return True only if all constraints are satisfied
        return (is_time_constraint_met and
                is_night_obs_constraint_met and
                is_avoid_sunrise_sunset_constraint_met)
    
    #----> A Method to check if a proposal can be scheduled <----#

    def can_be_scheduled_proposal(self, start_date: date, end_date: date) -> bool:
        """Check if a proposal can be scheduled based with the start and end dates."""
        for day in range((end_date - start_date).days + 1):  # Include the last day
            # Get the night window for the current day
            night_start_datetime, night_end_datetime = get_night_window(start_date + timedelta(days=day))
            sunrise_datetime, sunset_datetime = get_sunrise_sunset(start_date + timedelta(days=day))

            # Prepare the start times
            min_start_datetime = lst_to_utc(start_date + timedelta(days=day), self.lst_start_time)
            max_start_datetime = lst_to_utc(start_date + timedelta(days=day), self.lst_start_end_time)

            # Check both start times for night observations
            for start_datetime in [min_start_datetime, max_start_datetime]:
                # Check if scheduling within the night window is possible
                if self.night_obs:
                    if not (start_datetime >= night_start_datetime and 
                            start_datetime + timedelta(seconds=self.simulated_duration) <= night_end_datetime):
                        return False  # Constraint not met

                # Check for sunrise/sunset avoidance
                if self.avoid_sunrise_sunset:
                    if not (start_datetime + timedelta(seconds=self.simulated_duration) <= sunrise_datetime or 
                            start_datetime >= sunset_datetime):
                        return False  # Constraint not met

        return True  # All constraints met
    
    #----> A Method to read in a csv file of proposals and a method for filtering proposals <----#
    
    @staticmethod
    def read_proposals_from_csv(file_path: str) -> list["Proposal"]:

        proposals = []
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for id, row in enumerate(reader):
                prefered_dates_start = []
                prefered_dates_end = []
                avoid_dates_start = []
                avoid_dates_end = []

                # Read preferred dates
                i = 1
                while f'prefered_dates_start_{i}' in row:
                    prefered_dates_start.append(date.fromisoformat(row[f'prefered_dates_start_{i}']))
                    i += 1

                i = 1
                while f'prefered_dates_end_{i}' in row:
                    prefered_dates_end.append(date.fromisoformat(row[f'prefered_dates_end_{i}']))
                    i += 1

                # Read avoided dates
                i = 1
                while f'avoid_dates_start_{i}' in row:
                    avoid_dates_start.append(date.fromisoformat(row[f'avoid_dates_start_{i}']))
                    i += 1

                i = 1
                while f'avoid_dates_end_{i}' in row:
                    avoid_dates_end.append(date.fromisoformat(row[f'avoid_dates_end_{i}']))
                    i += 1
                if row['minimum_antennas'] == '':
                    continue # invalid data with missing key 'minimum_antennas'

                if int(row['simulated_duration']) < 60 * 30:
                    continue
                proposals.append(Proposal(
                    id = int(row['id']),
                    owner_email = row['owner_email'],
                    build_time = 30 * 60,
                    prefered_dates_start = prefered_dates_start,
                    prefered_dates_end = prefered_dates_end,
                    avoid_dates_start = avoid_dates_start,
                    avoid_dates_end = avoid_dates_end,
                    night_obs = True if str(row['night_obs']).lower() == "yes" else False,
                    avoid_sunrise_sunset = True if str(row['avoid_sunrise_sunset']).lower == "yes" else False,
                    minimum_antennas = int(row['minimum_antennas']),
                    lst_start_time = parse_time(row['lst_start']),
                    lst_start_end_time = parse_time(row['lst_start_end']),
                    simulated_duration = int(row['simulated_duration']),
                    score = get_score(str(row['proposal_id']))
                ))    
        return proposals
    
    @staticmethod
    def filter_proposals_by_date(proposals: list["Proposal"],start_date: date, end_date: date) -> list["Proposal"]:
        """Filter proposals based on the given date range.
        
        Args:
            proposals (list[Proposal]): List of proposals to filter.
            start_date (date): Start date of the range.
            end_date (date): End date of the range.
        
        Returns:
            list[Proposal]: Filtered list of proposals.
        """
        filtered_proposals: list[Proposal] = list()

        total_timetable_duration: int = (end_date - start_date).total_seconds()
        cumulative_timetable_duration: int = 0

        # Iterate through each proposal and check if it can be scheduled
        for proposal in proposals:

            if not Proposal.can_be_scheduled_proposal(proposal, start_date, end_date):  # Check if the proposal can be scheduled
                continue
            
            cumulative_timetable_duration += proposal.simulated_duration
            if cumulative_timetable_duration > total_timetable_duration * 0.85:
                break
            
            filtered_proposals.append(proposal) # Add the proposal if it can be scheduled
        return filtered_proposals
    
     
    # def get_proposal_by_id(self, proposal_id: int):
    #   return next((p for p in self.proposals if p.id == proposal_id), None)
