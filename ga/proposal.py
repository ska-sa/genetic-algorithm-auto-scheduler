from datetime import datetime, date, time, timedelta
import csv
import random
# from ga.utils import lst_to_utc, get_night_window, get_sunrise_sunset

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

    # def lst_start_end_time_constraint_met(self, start_datetime: datetime) -> bool:
    
    #     """Check if the proposal's start time is within the allowed LST start and end time.
        
    #     Args:
    #         proposal (Proposal): The proposal to check.
    #         start_datetime (datetime): The proposed start datetime.
        
    #     Returns:
    #         bool: True if the constraint is met, False otherwise.
    #     """
    #     self.lst_start_time = lst_to_utc(start_datetime.date(), self.lst_start_time) 
    #     self.lst_start_end_time = lst_to_utc(start_datetime.date(), self.lst_start_end_time)
    #     return self.lst_start_time <= start_datetime and start_datetime <= self.lst_start_end_time
     
    # def night_obs_constraint_met(self, start_datetime: datetime) -> bool:
    #     if self.night_obs:
    #         # Compute end datetime based on simulated duration
    #         end_datetime = start_datetime + timedelta(seconds=self.simulated_duration)
    #         night_start_datetime, night_end_datetime = get_night_window(start_datetime.date())

    #         # Check if both start and end datetimes fall within the night window
    #         if night_start_datetime <= start_datetime <= night_end_datetime and \
    #         night_start_datetime <= end_datetime <= night_end_datetime:
    #             return True  # Constraint met
    #         return False  # Constraint not met
    #     return True  # If night observations are not required, constraint is met

    # def avoid_sunrise_sunset_contraint_met(self, start_datetime: datetime) -> bool:
    #     if self.avoid_sunrise_sunset:
    #         # Get sunrise and sunset datetimes
    #         sunrise_datetime, sunset_datetime = get_sunrise_sunset(date=start_datetime.date())

    #         # Compute end datetime based on the proposal's duration
    #         end_datetime = start_datetime + timedelta(minutes=self.simulated_duration)

    #         # Check if sunrise or sunset occurs within the proposal's duration
    #         if (sunrise_datetime >= end_datetime) or (sunset_datetime <= start_datetime):
    #             return True  # Constraint met (neither occurs during the proposal)
    #         return False  # Constraint not met (one of them occurs during the proposal)
    #     return True  # If avoiding sunrise/sunset is not required, constraint is met

    # def all_constraints_met(self, start_datetime: datetime) -> bool:
    #     """
    #     Check if all constraints for the proposal are met.
        
    #     Parameters:
    #     proposal (Proposal): The proposal to check.
    #     start_datetime (datetime): The proposed start datetime.
        
    #     Returns:
    #     bool: True if all constraints are met, False otherwise.
    #     """
    #     return (self.lst_start_end_time_constraint_met(self, start_datetime) and
    #             self.night_obs_constraint_met(self, start_datetime) and
    #             self.avoid_sunrise_sunset_contraint_met(self, start_datetime)) 
    
    # def get_score(self) -> int:
    #     return 1
  
    # def can_be_scheduled_proposal(self, start_date: date, end_date: date) -> bool:
    #     """Check if a proposal can be scheduled based with the start and end dates."""
    #     for day in range((end_date - start_date).days + 1):  # Include the last day
    #         # Get the night window for the current day
    #         night_start_datetime, night_end_datetime = get_night_window(start_date + timedelta(days=day))
    #         sunrise_datetime, sunset_datetime = get_sunrise_sunset(start_date + timedelta(days=day))

    #         # Prepare the start times
    #         min_start_datetime = lst_to_utc(start_date + timedelta(days=day), self.lst_start_time)
    #         max_start_datetime = lst_to_utc(start_date + timedelta(days=day), self.lst_start_end_time)

    #         # Check both start times for night observations
    #         for start_datetime in [min_start_datetime, max_start_datetime]:
    #             # Check if scheduling within the night window is possible
    #             if self.night_obs:
    #                 if not (start_datetime >= night_start_datetime and 
    #                         start_datetime + timedelta(seconds=self.simulated_duration) <= night_end_datetime):
    #                     return False  # Constraint not met

    #             # Check for sunrise/sunset avoidance
    #             if self.avoid_sunrise_sunset:
    #                 if not (start_datetime + timedelta(seconds=self.simulated_duration) <= sunrise_datetime or 
    #                         start_datetime >= sunset_datetime):
    #                     return False  # Constraint not met

    #     return True  # All constraints met
    @staticmethod
    def parse_time(time_str: str) -> time:
        """
        Parse a time string in the format "HH:MM" and return a datetime.time object.
        """
        hour, minute = map(int, time_str.split(":"))
        return time(hour, minute)

    @staticmethod
    def get_score(prop_id: int) -> int:

        return random.randint(1, 4) # In future we have to classify proposals to get their actual rates
    # def get_proposal_by_id(self, proposal_id: int):
    #    return next((p for p in self.proposals if p.id == proposal_id), None)

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
                    lst_start_time = Proposal.parse_time(row['lst_start']),
                    lst_start_end_time = Proposal.parse_time(row['lst_start_end']),
                    simulated_duration = int(row['simulated_duration']),
                    score = Proposal.get_score(str(row['proposal_id']))
                ))    
        return proposals
    
    # def filter_proposals_by_date(self, start_date: date, end_date: date) -> list["Proposal"]:
    #     """Filter proposals based on the given date range.
        
    #     Args:
    #         proposals (list[Proposal]): List of proposals to filter.
    #         start_date (date): Start date of the range.
    #         end_date (date): End date of the range.
        
    #     Returns:
    #         list[Proposal]: Filtered list of proposals.
    #     """
    #     filtered_proposals: list[Proposal] = list()

    #     total_timetable_duration: int = (end_date - start_date).total_seconds()
    #     cumulative_timetable_duration: int = 0

    #     # Iterate through each proposal and check if it can be scheduled
    #     for proposal in self.proposals:

    #         if not self.can_be_scheduled_proposal(proposal, start_date, end_date):  # Check if the proposal can be scheduled
    #             continue
            
    #         cumulative_timetable_duration += proposal.simulated_duration
    #         if cumulative_timetable_duration > total_timetable_duration * 0.85:
    #             break
            
    #         filtered_proposals.append(proposal) # Add the proposal if it can be scheduled
    #     return filtered_proposals
    
     
    