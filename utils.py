import random
import csv
from datetime import datetime, date, time, timedelta
from classes.timeslot import Timeslot
from classes.proposal import Proposal


def read_proposals_from_csv(file_path: str) -> list[Proposal]:
    proposals = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
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
                int(row['id']),
                row['owner_email'],
                30 * 60,
                prefered_dates_start,
                prefered_dates_end,
                avoid_dates_start,
                avoid_dates_end,
                True if str(row['night_obs']).capitalize() == "Yes" else False,
                True if str(row['avoid_sunrise_sunset']).capitalize == "Yes" else False,
                int(row['minimum_antennas']),
                Proposal.parse_time(row['lst_start']),
                Proposal.parse_time(row['lst_start_end']),
                int(row['simulated_duration']),
                get_score(str(row['proposal_id']))
            ))

    return proposals

def get_score(proposal_id: str):
    return random.randint(1, 4) # In future we have to classify proposals to get their actual rates