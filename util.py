from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
from pathlib import Path
import datetime
from datetime import timedelta
import random
from tqdm import tqdm

from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

from intervaltree import Interval, IntervalTree
import lstpressure

from constants import HARD_CONSTRAINT_PENALTY, SKA_LONGITUDE, SKA_LATITUDE, LST_HOURS_IN_DAY
from heuristics import get_first_slot_within_time_constraints

def LST_to_UTC(lst_hours: float, date: datetime.datetime, longitude: float = SKA_LONGITUDE) -> int:
    """Convert Local Sidereal Time (LST) to UTC.

    Args:
        lst_hours (float): Time in LST, in sidereal hours since 12am LST.
        date (datetime): Date on which to calculate the UTC time.
        longitude (float): Longitude used to calculate UTC. Must be given as a float in degrees. For example, -30.0 for 30 degrees west. Defaults to the longitude of the SKA site as used in OPT (21.44389).

    Returns:
        datetime: A UTC timestamp that corresponds to the given LST.
    """

    # print(f"Converting LST {lst_hours} hours to UTC on date {date} with longitude {longitude}")

    return lstpressure.sun.location_providers.meerkat_provider.DateTimeUtils.DateTimeUtil.lst2ut(
            lst_hours, longitude, date
        )

import datetime
import math

def UTC_to_LST(utc_dt, longitude=SKA_LONGITUDE):
    """
    Converts a UTC datetime object to Local Sidereal Time (LST).

    Args:
        utc_dt (datetime.datetime): The Coordinated Universal Time. 
                                     It's crucial that this datetime object 
                                     represents UTC and is timezone-naive or
                                     explicitly set to UTC.
        longitude (float): The observer's longitude in degrees 
                           (East is positive, West is negative).

    Returns:
        float: The Local Sidereal Time in hours.
    """

    # Ensure we have a datetime object
    if not isinstance(utc_dt, datetime.datetime):
        raise TypeError("utc_dt must be a datetime.datetime object")

    # --- 1. Calculate Julian Date (JD) ---
    year = utc_dt.year
    month = utc_dt.month
    day = utc_dt.day
    hour = utc_dt.hour
    minute = utc_dt.minute
    second = utc_dt.second

    if month <= 2:
        year -= 1
        month += 12

    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    
    # JD at 0h UTC
    jd0 = math.floor(365.25 * (year + 4716)) + \
          math.floor(30.6001 * (month + 1)) + \
          day + b - 1524.5
          
    # Fractional part of the day
    day_fraction = (hour + minute / 60.0 + second / 3600.0) / 24.0

    # Full Julian Date
    jd = jd0 + day_fraction

    # --- 2. Calculate Greenwich Mean Sidereal Time (GMST) ---
    # T = Julian centuries since J2000.0
    t = (jd - 2451545.0) / 36525.0

    # GMST at 0h UTC in degrees (using IAU 1982 formula)
    gmst0_deg = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + \
                0.000387933 * t**2 - t**3 / 38710000.0

    # Convert GMST to hours and normalize
    gmst_hours = (gmst0_deg / 15.0) % 24.0 # 1 hour = 15 degrees
    if gmst_hours < 0:
        gmst_hours += 24

    # --- 3. Calculate Local Sidereal Time (LST) ---
    # Convert longitude to hours
    lon_hours = longitude / 15.0

    # Calculate LST
    lst_hours = gmst_hours + lon_hours

    # Normalize LST to 0-24 hours
    lst_hours = lst_hours % 24.0
    if lst_hours < 0:
        lst_hours += 24
        
    return lst_hours

def format_hms(hours):
    """Formats decimal hours into H:M:S string."""
    h = int(hours)
    minutes_decimal = (hours - h) * 60
    m = int(minutes_decimal)
    seconds_decimal = (minutes_decimal - m) * 60
    s = round(seconds_decimal, 2)
    return f"{h:02d}h {m:02d}m {s:05.2f}s"

def read_observation_list_file(observation_list: Path, limits=None) -> list[dict]:
    with observation_list.open(mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        # type cast columns
        rows = []
        for row in reader:
            row['simulated_duration'] = int(row['simulated_duration'])
            # if the minimum antennas is empty then default to 64
            row['minimum_antennas'] = int(row['minimum_antennas']) if row['minimum_antennas'] != '' else 64
            row['lst_start'] = convert_lst_string_to_hours(row['lst_start'])
            row['lst_start_end'] = convert_lst_string_to_hours(row['lst_start_end'])
            rows.append(row)
        if limits:
            return rows[limits[0]:limits[1]]
        return rows
        

def get_UTC_sunrise_sunset_times(
    date: datetime,
    num_days: int = 1,
    latitude: float = SKA_LATITUDE,
    longitude: float = SKA_LONGITUDE,
):
    """Get the sunrise and sunset times at the SKA site in UTC on a specific day.

    Args:
        date (datetime.datetime): The date to query for
        num_days (int, optional): How many days to fetch sunrise/sunset times for. Defaults to 1.
        latitude (float, optional): Latitude to use when getting sunrise/sunset times. Defaults to the latitude of the SKA site as used in OPT (-30.71105).
        longitude (float, optional): Longitude to use when getting sunrise/sunset times. Defaults to the longitude of the SKA site as used in OPT (21.44389).

    Returns:
        list: List of dicts which each represent a date, with `date`, `sunrise` and `sunset` properties. All times are in UTC.
    """

    # If needs be, we can get sunrise/sunset times for the whole week
    date_start = date
    date_end = date + timedelta(days=num_days - 1)

    calendar = [
        d.dt.strftime("%Y-%m-%d")
        for d in lstpressure.LSTCalendar(date_start, date_end).dates
    ]

    times = []

    for date in calendar:

        sun_info = lstpressure.Sun(
            yyyymmdd=date.replace(
                "-", ""
            ),  # change format from YYYY-MM-DD to YYYYMMDD which is what lstpressure expects
            latitude=latitude,
            longitude=longitude,
        )
        times.append(
            {
                "date": date,  # returned date is still in YYYY-MM-DD format though
                "sunrise": sun_info.sunrise,
                "sunset": sun_info.sunset,
            }
        )

    times = sorted(times, key=lambda x: x["date"])

    return times


def sunrise_and_sunset_times_to_interval_tree(date, num_days):
    sunrise_sunset_times = get_UTC_sunrise_sunset_times(date, num_days)
    
    day_time_intervals = []
    sunrise_sunset_intervals = []
    for i, time in enumerate(sunrise_sunset_times):
        lst_sunrise = UTC_to_LST(time['sunrise'])
        lst_sunset = UTC_to_LST(time['sunset'])

        if lst_sunrise > lst_sunset:
            day_time_interval = Interval(lst_sunrise + (LST_HOURS_IN_DAY*i), 
                                        lst_sunset + (LST_HOURS_IN_DAY*(i+1)),
                                        f'Day {i+1} daylight')
        else:
            day_time_interval = Interval(lst_sunrise + (LST_HOURS_IN_DAY*i), 
                                        lst_sunset + (LST_HOURS_IN_DAY*(i)),
                                        f'Day {i+1} daylight')
        day_time_intervals.append(day_time_interval)

        sunrise_interval = Interval(lst_sunrise + (LST_HOURS_IN_DAY*i) - 0.25,
                                    lst_sunrise + (LST_HOURS_IN_DAY*i)+ 0.25,
                                    f'Day {i+1} sunrise')
        sunset_interval = Interval(lst_sunset + (LST_HOURS_IN_DAY*i) - 0.25,
                                   lst_sunset + (LST_HOURS_IN_DAY*i) + 0.25,
                                   f'Day {i+1} sunset')

        sunrise_sunset_intervals.append(sunrise_interval)
        sunrise_sunset_intervals.append(sunset_interval)
    day_time_interval_tree = IntervalTree(day_time_intervals)
    sunrise_sunset_interval_tree = IntervalTree(sunrise_sunset_intervals)

    return day_time_interval_tree, sunrise_sunset_interval_tree

def convert_lst_string_to_hours(lst_time):
    hours, minutes = map(int, lst_time.strip().split(":"))
    return hours + minutes / 60.0

def determine_schedule_fitness(schedule: list[int | None], unable_to_be_placed_observations: list[int]):
    fitness = len(unable_to_be_placed_observations) * HARD_CONSTRAINT_PENALTY

    # print("Fitness after hard constraint penalties")
    # print(fitness)

    unallocated_time = 0 # soft constraint to rank solutions against each other

    current_schedule_index = 0
    while current_schedule_index < len(schedule):
        # Save any unallocated time
        if schedule[current_schedule_index] is None:
            unallocated_time += 1
        current_schedule_index += 1

    # print("Unallocated time")
    # print(unallocated_time)

    fitness += unallocated_time

    return fitness

def visualize_schedule(date, impossible_to_place_observations, unable_to_be_placed_observations, schedule, fitness, slot_duration_s, slots_per_day, output_path="calendar_schedule.png"):
    num_days = math.ceil(len(schedule) / slots_per_day)
    hours_per_day = 24  # LST approximation

    fig, ax = plt.subplots(figsize=(2.5 * num_days, 12))

    # Colors per obs ID
    obs_ids = list(set(filter(None, schedule)))
    colors = {obs_id: f"#{random.randint(0, 0xFFFFFF):06x}" for obs_id in obs_ids}

    for i, obs_id in enumerate(schedule):
        if obs_id is None:
            continue

        day = i // slots_per_day
        slot_in_day = i % slots_per_day
        start_hour = (slot_in_day * slot_duration_s) / 3600
        end_hour = ((slot_in_day + 1) * slot_duration_s) / 3600

        # Create rectangle: (x=day, y=start_hour, width=1, height=slot_duration_h)
        ax.add_patch(Rectangle(
            (day, start_hour),
            1,
            end_hour - start_hour,
            color=colors[obs_id],
            alpha=0.7,
            edgecolor="black"
        ))

        # Optional: add text label only once per continuous block
        # Check if this is the first slot or the previous one is different
        if i == 0 or schedule[i-1] != obs_id:
            ax.text(
                day + 0.5,
                start_hour + 0.1,
                obs_id,
                ha="center",
                va="top",
                fontsize=8,
                color="black",
                rotation=0,
                weight="bold"
            )

    ax.set_xlim(0, num_days)
    ax.set_ylim(0, hours_per_day)
    ax.invert_yaxis()
    ax.set_xticks(range(num_days))
    ax.set_xticklabels([f"Day {i+1}" for i in range(num_days)])
    ax.set_yticks(range(0, hours_per_day + 1, 2))
    ax.set_yticklabels([f"{h}:00" for h in range(0, hours_per_day + 1, 2)])
    ax.set_xlabel("Day")
    ax.set_ylabel("LST Time")
    ax.set_title(f"MeerKAT Observation Calendar ({date}) (Fitness={fitness}) (Unabled to place = {len(unable_to_be_placed_observations)}) (Impossible = {len(impossible_to_place_observations)})")
    ax.grid(True, axis='y', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved calendar visualization to {output_path}")

def compute_fitness(individual, observation_list):
    return individual, individual.fitness(observation_list)

def evaluate_population_fitnesses(population, observation_list, minimize_fitness):
    results = {}

    # Assign unique IDs to individuals if they don't have them
    for i, ind in enumerate(population):
        ind._id = i

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(compute_fitness, ind, observation_list): ind._id
            for ind in population if ind._fitness is None
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Evaluating fitnesses"):
            individual, fitness_value = future.result()
            results[individual._id] = fitness_value

    # Assign fitness back to each individual
    for ind in population:
        if ind._id in results:
            ind._fitness = results[ind._id]

    # Sort using cached fitness
    sorted_population = sorted(
        population,
        key=lambda ind: ind._fitness,
        reverse=minimize_fitness
    )

    return sorted_population

def filter_out_impossible_to_place_obs(observations,
                                       empty_schedule,
                                       slots_per_day,
                                       schedule_slot_duration_s,
                                       day_time_interval_tree,
                                       sunrise_sunset_interval_tree,
                                       antenna_available):
    # Compute impossible to place observations
    impossible_to_place_observations = []
    possible_to_place_observations = []
    for observation in observations:
        duration_s = observation.get('simulated_duration')
        # check if observation an be placed in an empty schedule
        start_t, end_t = get_first_slot_within_time_constraints(empty_schedule,
                                                                slots_per_day,
                                                                schedule_slot_duration_s,
                                                                duration_s,
                                                                observation,
                                                                day_time_interval_tree,
                                                                sunrise_sunset_interval_tree,
                                                                antenna_available,)
        if start_t is None and end_t is None:
            impossible_to_place_observations.append(observation)
        else:
            possible_to_place_observations.append(observation)
    
    return possible_to_place_observations, impossible_to_place_observations


if __name__ == '__main__':
    date = datetime.datetime.strptime('2025-05-01', '%Y-%m-%d')
    sunrise_and_sunset_times_to_interval_tree(date, 4)
