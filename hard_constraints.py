import datetime

def convert_slots_to_lst_hours(slot: int, required_slots: int, slot_length: int) -> tuple[datetime.time, datetime.time]:
  # Calculate the start time in seconds from midnight
  start_seconds = slot * slot_length

  # Calculate the end time in seconds from midnight
  end_seconds = (slot + required_slots) * slot_length

  # Return the lst hours for slot start and end
  return start_seconds / 3600, end_seconds / 3600


def check_night_time_constraint(observation, day_time_interval_tree, slot, required_slots, slot_length):
    is_night_obs = observation.get('night_obs') == 'Yes'

    # If this observation doesn't need to be at night, the constraint is met.
    if not is_night_obs:
        return True

    lst_start_hours, lst_end_hours = convert_slots_to_lst_hours(slot, required_slots, slot_length) 

    is_scheduled_during_night = not day_time_interval_tree.overlap(lst_start_hours, lst_end_hours)

    return is_scheduled_during_night


def check_avoid_sunset_constraint(observation, sunrise_sunset_interval_tree, slot, required_slots, slot_length):
    avoid_sunrise_sunset = observation.get('avoid_sunrise_sunset') == 'Yes'

    # If this observation doesn't need to be at night, the constraint is met.
    if not avoid_sunrise_sunset:
        return True

    lst_start_hours, lst_end_hours = convert_slots_to_lst_hours(slot, required_slots, slot_length) 

    is_scheduled_during_night = not sunrise_sunset_interval_tree.overlap(lst_start_hours, lst_end_hours)

    return is_scheduled_during_night


def check_minimum_antennas(observation, antennas_available=64):
    minimum_antennas = int(observation.get('minimum_antennas'))

    return antennas_available >= minimum_antennas

def check_all_hard_constraints(
        observation,
        day_time_interval_tree,
        sunrise_sunset_interval_tree,
        antennas_available,
        slot,
        required_slots,
        slot_length):
    if not check_night_time_constraint(observation, day_time_interval_tree, slot, required_slots, slot_length):
        # print("Failed night time constraint")
        return False

    if not check_avoid_sunset_constraint(observation, sunrise_sunset_interval_tree, slot, required_slots, slot_length):
        # print("Failed sunrise sunset constraint")
        return False

    if not check_minimum_antennas(observation, antennas_available):
        # print("Failed check minimum antennas")
        return False

    return True
