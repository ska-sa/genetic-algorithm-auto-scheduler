from random import choice
import time
from hard_constraints import check_all_hard_constraints
from intervaltree import IntervalTree

# ========================
# Observation heuristics
# ========================
def get_shortest_observation_block(observations: list[dict]) -> dict:
    shortest_block_index = 0
    shortest_block_duration = observations[0]["simulated_duration"]

    for i, block in enumerate(observations):
        if block["simulated_duration"] < shortest_block_duration:
            shortest_block_index = i
            shortest_block_duration = block["simulated_duration"]

    return shortest_block_index

def get_longest_observation_block(observations: list[dict]) -> dict:
    longest_block_index = 0
    longest_block_duration = 0

    for i, block in enumerate(observations):
        if block["simulated_duration"] < longest_block_duration:
            longest_block_index = i
            longest_block_duration = block["simulated_duration"]

    return longest_block_index

def get_observation_block_with_min_antenna(observations: list[dict]) -> dict:
    min_antenna_block_index = 0
    min_num_antenna = observations[min_antenna_block_index]['minimum_antennas']

    for i, block in enumerate(observations):
        if min_num_antenna < block['minimum_antennas']:
            min_antenna_block_index = i
            min_num_antenna = block['minimum_antennas']

    return min_antenna_block_index

def get_observation_block_with_max_antenna(observations: list[dict]) -> dict:
    max_antenna_block_index = 0
    max_num_antenna = observations[max_antenna_block_index]['minimum_antennas']

    for i, block in enumerate(observations):
        if max_num_antenna < block['minimum_antennas']:
            max_antenna_block_index = i
            max_num_antenna = block['minimum_antennas']

    return max_antenna_block_index

def get_observation_block_with_earliest_start_time(observations: list[dict]) -> dict:
    earliest_start_time_block_index = 0
    earliest_start_time = observations[earliest_start_time_block_index]['lst_start']

    for i, block in enumerate(observations):
        block_lst_start_int = block['lst_start']

        if earliest_start_time < block_lst_start_int:
            earliest_start_time_block_index = i
            earliest_start_time = block['lst_start']

    return earliest_start_time_block_index

def get_observation_block_with_latest_start_time(observations: list[dict]) -> dict:
    latest_start_time_block_index = 0
    latest_start_time = observations[latest_start_time_block_index]['lst_start']

    for i, block in enumerate(observations):
        if latest_start_time > block['lst_start']:
            latest_start_time_block_index = i
            latest_start_time = block['lst_start']

    return latest_start_time_block_index

def get_random_observation_block(observations: list[dict]):
    return choice(range(len(observations))) if observations else None

def get_random_night_observation_block(observations: list[dict]):
    night_blocks = [i for i, obs in enumerate(observations) if obs.get('night_obs').strip().lower() == 'yes']
    return choice(night_blocks) if night_blocks else None

def get_shortest_night_observation_block(observations: list[dict]):
    night_blocks = [(i, obs) for i, obs in enumerate(observations) if obs.get('night_obs').strip().lower() == 'yes']
    if not night_blocks:
        return None
    shortest = min(night_blocks, key=lambda x: x[1]['simulated_duration'])
    return shortest[0]

def get_longest_night_observation_block(observations: list[dict]):
    night_blocks = [(i, obs) for i, obs in enumerate(observations) if obs.get('night_obs').strip().lower() == 'yes']
    if not night_blocks:
        return None
    longest = max(night_blocks, key=lambda x: x[1]['simulated_duration'])
    return longest[0]

def get_night_observation_block_with_earliest_start_time(observations: list[dict]):
    night_blocks = [(i, obs) for i, obs in enumerate(observations) if obs.get('night_obs').strip().lower() == 'yes']
    if not night_blocks:
        return None
    earliest = min(night_blocks, key=lambda x: x[1]['lst_start'])
    return earliest[0]

def get_night_observation_block_with_latest_start_time(observations: list[dict]):
    night_blocks = [(i, obs) for i, obs in enumerate(observations) if obs.get('night_obs').strip().lower() == 'yes']
    if not night_blocks:
        return None
    latest = max(night_blocks, key=lambda x: x[1]['lst_start'])
    return latest[0]

# ========================
# Schedule slot heuristics
# ========================
def get_first_slot_within_time_constraints(schedule: list, slots_per_day: int, schedule_slot_duration_s: float, duration_seconds: int, observation: dict, day_time_interval_tree: IntervalTree, sunrise_sunset_interval_tree: IntervalTree, antenna_available: int) -> int:
    """Find the index of the first contiguous block of available slots based."""
    required_slots = duration_seconds // schedule_slot_duration_s

    for i in range(len(schedule) - required_slots + 1):
        if all(slot is None for slot in schedule[i:i + required_slots]):
            slot_start_time = ((i % slots_per_day) * schedule_slot_duration_s) / 3600
            if observation["lst_start"] <= slot_start_time <= observation["lst_start_end"]:
                # start_time = time.time()
                if check_all_hard_constraints(observation,
                                              day_time_interval_tree,
                                              sunrise_sunset_interval_tree,
                                              antenna_available,
                                              i,
                                              required_slots,
                                              schedule_slot_duration_s):
                    # print(f"Took {time.time() - start_time:.4f}s to check hard constraints (first slot)")
                    return i, i+required_slots
                # print(f"Took {time.time() - start_time:.4f}s to check hard constraints (first slot)")
    return None, None

def get_last_slot_within_time_constraints(schedule: list, slots_per_day: int, schedule_slot_duration_s: float, duration_seconds: int, observation: dict, day_time_interval_tree: IntervalTree, sunrise_sunset_interval_tree: IntervalTree, antenna_available: int) -> int:
    """Find the index of the last contiguous block of available slots based."""
    required_slots = duration_seconds // schedule_slot_duration_s

    for i in reversed(range(len(schedule) - required_slots + 1)):
        if all(slot is None for slot in schedule[i:i + required_slots]):
            slot_start_time = ((i % slots_per_day) * schedule_slot_duration_s) / 3600
            if observation["lst_start"] <= slot_start_time <= observation["lst_start_end"]:
                # start_time = time.time()
                if check_all_hard_constraints(observation,
                                              day_time_interval_tree,
                                              sunrise_sunset_interval_tree,
                                              antenna_available,
                                              i,
                                              required_slots,
                                              schedule_slot_duration_s):
                    # print(f"Took {time.time() - start_time:.4f}s to check hard constraints (last slot)")
                    return i, i+required_slots
                # print(f"Took {time.time() - start_time:.4f}s to check hard constraints (last slot)")
    return None, None

def get_random_slot_within_time_constraints(schedule: list, slots_per_day: int, schedule_slot_duration_s: float, duration_seconds: int, observation: dict, day_time_interval_tree: IntervalTree, sunrise_sunset_interval_tree: IntervalTree, antenna_available: int) -> int:
    """Find a start index of a random contiguous block of available slots."""
    required_slots = duration_seconds // schedule_slot_duration_s
    valid_indices = []
    # start_time = time.time()

    for i in range(len(schedule) - required_slots + 1):
        if all(slot is None for slot in schedule[i:i + required_slots]):
            slot_start_time = ((i % slots_per_day) * schedule_slot_duration_s) / 3600
            if observation["lst_start"] <= slot_start_time <= observation["lst_start_end"]:
                if check_all_hard_constraints(observation,
                                              day_time_interval_tree,
                                              sunrise_sunset_interval_tree,
                                              antenna_available,
                                              i,
                                              required_slots,
                                              schedule_slot_duration_s):
                    valid_indices.append(i)
    # print(f"Took {time.time() - start_time:.4f}s to check hard constraints (random)")

    if not valid_indices:
        return None, None

    start_idx = choice(valid_indices)
    return start_idx, start_idx + required_slots

def get_smallest_possible_slot_within_time_constraints(schedule: list, slots_per_day: int, schedule_slot_duration_s: float, duration_seconds: int, observation: dict, day_time_interval_tree: IntervalTree, sunrise_sunset_interval_tree: IntervalTree, antenna_available: int) -> int:
    """Find the start index of the smallest valid contiguous slot (first tight fit)."""
    required_slots = duration_seconds // schedule_slot_duration_s
    best_start = None
    shortest_block_len = None

    for i in range(len(schedule) - required_slots + 1):
        if all(slot is None for slot in schedule[i:i + required_slots]):
            slot_start_time = ((i % slots_per_day) * schedule_slot_duration_s) / 3600
            if observation["lst_start"] <= slot_start_time <= observation["lst_start_end"]:
                if check_all_hard_constraints(observation,
                                              day_time_interval_tree,
                                              sunrise_sunset_interval_tree,
                                              antenna_available,
                                              i,
                                              required_slots,
                                              schedule_slot_duration_s):

                    # Check how far the free block actually continues
                    current_length = 0
                    for j in range(i, len(schedule)):
                        if schedule[j] is None:
                            current_length += 1
                        else:
                            break

                    if shortest_block_len is None or current_length < shortest_block_len:
                        best_start = i
                        shortest_block_len = current_length

    if best_start is not None:
        return best_start, best_start + required_slots

    return None, None

def get_biggest_possible_slot_within_time_constraints(
    schedule: list,
    slots_per_day: int,
    schedule_slot_duration_s: float,
    duration_seconds: int,
    observation: dict,
    day_time_interval_tree: IntervalTree,
    sunrise_sunset_interval_tree: IntervalTree,
    antenna_available: int
) -> int:
    """Find the start index of the longest valid contiguous block of available slots that fits the observation."""

    required_slots = duration_seconds // schedule_slot_duration_s
    best_start = None
    longest_block_len = 0

    for i in range(len(schedule) - required_slots + 1):
        if all(slot is None for slot in schedule[i:i + required_slots]):
            slot_start_time = ((i % slots_per_day) * schedule_slot_duration_s) / 3600
            if observation["lst_start"] <= slot_start_time <= observation["lst_start_end"]:
                if check_all_hard_constraints(observation,
                                              day_time_interval_tree,
                                              sunrise_sunset_interval_tree,
                                              antenna_available,
                                              i,
                                              required_slots,
                                              schedule_slot_duration_s):

                    # Check how far the free block actually continues
                    current_length = 0
                    for j in range(i, len(schedule)):
                        if schedule[j] is None:
                            current_length += 1
                        else:
                            break

                    if current_length > longest_block_len:
                        best_start = i
                        longest_block_len = current_length

    if best_start is not None:
        return best_start, best_start + required_slots

    return None, None
