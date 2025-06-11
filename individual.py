from copy import deepcopy
import datetime
from math import floor
from pathlib import Path
from random import randint, random
from intervaltree import IntervalTree

from heuristics import (
    get_first_slot_within_time_constraints,
    get_last_slot_within_time_constraints,
    get_longest_night_observation_block,
    get_longest_observation_block,
    get_night_observation_block_with_earliest_start_time,
    get_night_observation_block_with_latest_start_time,
    get_observation_block_with_earliest_start_time,
    get_observation_block_with_latest_start_time,
    get_observation_block_with_max_antenna,
    get_observation_block_with_min_antenna,
    get_random_night_observation_block,
    get_random_observation_block,
    get_random_slot_within_time_constraints,
    get_shortest_night_observation_block,
    get_shortest_observation_block,
    get_smallest_possible_slot_within_time_constraints,
    get_biggest_possible_slot_within_time_constraints,
)
from util import determine_schedule_fitness, filter_out_impossible_to_place_obs, read_observation_list_file, sunrise_and_sunset_times_to_interval_tree, visualize_schedule

class Individual:
    def __init__(self, heuristics_combination_length: int, day_time_interval_tree: IntervalTree, sunrise_sunset_interval_tree: IntervalTree, antenna_available: int, schedule_slot_duration_s: float = 60):
        assert schedule_slot_duration_s % 60 == 0, "Schedule slot duration is not a multiple of 60."

        self._schedule_slot_duration_s = schedule_slot_duration_s
        self._day_time_interval_tree = day_time_interval_tree
        self._sunrise_sunset_interval_tree = sunrise_sunset_interval_tree
        self._antenna_available = antenna_available

        # 23 + 56/60 since lst time has 23h56m in a day
        self._slots_per_day = floor(((23 + 56/60)*3600) / self._schedule_slot_duration_s)
        self._schedule: list[None | str] = self._empty_schedule()
        self._fitness = None

        self._available_observation_block_heuristics: list[int] = [
            get_shortest_observation_block,
            get_longest_observation_block,
            get_observation_block_with_min_antenna,
            get_observation_block_with_max_antenna,
            get_observation_block_with_earliest_start_time,
            get_observation_block_with_latest_start_time,
            get_random_observation_block,
            get_random_night_observation_block,
            get_shortest_night_observation_block,
            get_longest_night_observation_block,
            get_night_observation_block_with_earliest_start_time,
            get_night_observation_block_with_latest_start_time,
        ]
        self._available_timetable_slot_heuristics: list[int] = [
            get_first_slot_within_time_constraints,
            get_last_slot_within_time_constraints,
            get_random_slot_within_time_constraints,
            get_smallest_possible_slot_within_time_constraints,
            get_biggest_possible_slot_within_time_constraints,
        ]

        self._heuristics_combination_length = heuristics_combination_length
        self._observation_block_heuristics: list[int] = [
            randint(0, len(self._available_observation_block_heuristics)-1)
            for _ in range(heuristics_combination_length)
        ]
        self._timetable_slot_heuristics: list[int] = [
            randint(0, len(self._available_timetable_slot_heuristics)-1)
            for _ in range(heuristics_combination_length)
        ]

        self._dna: list[int] = self._observation_block_heuristics + self._timetable_slot_heuristics

    def mutate(self, mutation_rate: float = 0.1) -> "Individual":
        """Mutate a copy of the individual by randomly tweaking its DNA."""
        new = deepcopy(self)
        new._fitness = None
        for i in range(len(new._dna)):
            if random() < mutation_rate:
                if i < self._heuristics_combination_length:
                    new._dna[i] = randint(0, len(self._available_observation_block_heuristics) - 1)
                else:
                    new._dna[i] = randint(0, len(self._available_timetable_slot_heuristics) - 1)

        new._observation_block_heuristics = new._dna[:self._heuristics_combination_length]
        new._timetable_slot_heuristics = new._dna[self._heuristics_combination_length:]
        return new

    def crossover(self, other: "Individual") -> tuple["Individual", "Individual"]:
        """Single-point crossover."""
        point = randint(1, len(self._dna) - 2)
        child1_dna = self._dna[:point] + other._dna[point:]
        child2_dna = other._dna[:point] + self._dna[point:]

        child1 = deepcopy(self)
        child1._dna = child1_dna
        child1._observation_block_heuristics = child1_dna[:self._heuristics_combination_length]
        child1._timetable_slot_heuristics = child1_dna[self._heuristics_combination_length:]
        child1._fitness = None

        child2 = deepcopy(other)
        child2._dna = child2_dna
        child2._observation_block_heuristics = child2_dna[:self._heuristics_combination_length]
        child2._timetable_slot_heuristics = child2_dna[self._heuristics_combination_length:]
        child2._fitness = None

        return child1, child2
    
    def build_schedule(self, observations: list[dict]) -> tuple[list[None | str], set]:
        observations_left = observations.copy()
        schedule = self._empty_schedule()
        unable_to_be_placed_observations = set()
        fail_to_pick_observation_counter = 0

        current_heuristic_index = 0

        while len(observations_left) > 0:
            if fail_to_pick_observation_counter > len(self._observation_block_heuristics):
                print(f"Failed to pick a new observation with any of the heuristics ({fail_to_pick_observation_counter})")
                for obs in observations_left:
                    unable_to_be_placed_observations.add(obs["id"])
                break

            # Choose observation using the selected heuristic
            # start_time = time.time()
            obs_idx = self._available_observation_block_heuristics[
                self._observation_block_heuristics[current_heuristic_index]
            ](observations_left)
            # print(f"Took {time.time() - start_time:.4f}s to get obs index")

            if obs_idx is None:
                # print("obs_idx is None with heuristic", self._observation_block_heuristics[current_heuristic_index])
                current_heuristic_index = (current_heuristic_index + 1) % self._heuristics_combination_length
                fail_to_pick_observation_counter += 1
                continue

            fail_to_pick_observation_counter = 0

            obs = observations_left[obs_idx]
            duration_s = obs["simulated_duration"]

            # Choose where to put it in the schedule
            # start_time = time.time()
            start_slot, end_slot = self._available_timetable_slot_heuristics[
                self._timetable_slot_heuristics[current_heuristic_index]
            ](
                schedule,
                self._slots_per_day,
                self._schedule_slot_duration_s,
                duration_s,
                obs,
                self._day_time_interval_tree,
                self._sunrise_sunset_interval_tree,
                self._antenna_available,
            )
            # print(f"Took {time.time() - start_time:.4f}s to get schedule slot index")

            if start_slot is None and end_slot is None:
                # print(f"start_slot is None and end_slot is None")
                unable_to_be_placed_observations.add(obs["id"])
                observations_left.pop(obs_idx)
                continue

            # Assign it
            for j in range(start_slot, end_slot):
                schedule[j] = obs["id"]

            observations_left.pop(obs_idx)
            current_heuristic_index = (current_heuristic_index + 1) % self._heuristics_combination_length
        

        return schedule, unable_to_be_placed_observations

    def fitness(self, observations: list[dict]) -> float:
        if self._fitness is not None:
            return self._fitness

        schedule, unable_to_be_placed_observations = self.build_schedule(observations)
        self._fitness = determine_schedule_fitness(schedule, unable_to_be_placed_observations)
        return self._fitness

    def _empty_schedule(self) -> list[None | str]:
        return [None] * (7 * self._slots_per_day)


class TestIndividual:
    def __init__(self, dna_length: int, sunrise_sunset_intervals: list[tuple] = (), antenna_available: int = 0):
        self._dna: list[int] = [
            randint(0, 9)
            for _ in range(dna_length)
        ]

        self._fitness = None

    def mutate(self, mutation_rate: float = 0.1) -> "TestIndividual":
        """Mutate a copy of the individual by randomly tweaking its DNA."""
        new = deepcopy(self)
        new._fitness = None
        new._fitness = None
        for i in range(len(new._dna)):
            if random() < mutation_rate:
                new._dna[i] = randint(0, 9)
        return new

    def crossover(self, other: "TestIndividual") -> tuple["TestIndividual", "TestIndividual"]:
        """Single-point crossover."""
        point = randint(1, len(self._dna) - 2)
        child1_dna = self._dna[:point] + other._dna[point:]
        child2_dna = other._dna[:point] + self._dna[point:]

        child1 = deepcopy(self)
        child1._fitness = None
        child2 = deepcopy(other)
        child2._fitness = None
        child1._dna = child1_dna
        child2._dna = child2_dna
        return child1, child2

    def fitness(self, observations: list[dict] = None) -> float:
        """Simple fitness function: sum of the DNA."""
        if self._fitness is None:
            self._fitness = sum(self._dna)
        return self._fitness

if __name__=="__main__":
    # individual_a = TestIndividual(10)
    # individual_a._dna = [0] * 10

    # individual_b = TestIndividual(10)
    # individual_b._dna = [9] * 10

    # =============================
    # Test observation individuals
    # =============================
    date = datetime.datetime.strptime('2025-05-01', '%Y-%m-%d')
    day_time_interval_tree, sunrise_sunset_interval_tree = sunrise_and_sunset_times_to_interval_tree(date, 4)

    observations = read_observation_list_file(Path("ObsList1737538994939.csv"))
    # observations = read_observation_list_file(Path("ObsList1737538994939.csv"), limits=[1, 21])
    # observations = read_observation_list_file(Path("ObsList1737538994939.csv"), limits=[22, 72])

    # individual_a = Individual(5, day_time_interval_tree, sunrise_sunset_interval_tree, 64)
    # individual_b = Individual(5, day_time_interval_tree, sunrise_sunset_interval_tree, 64)

    # print("Individual A")
    # print("=============")
    # print("DNA:", individual_a._dna)
    # print("Fitness:", individual_a.fitness(observations))

    # print("\nIndividual B")
    # print("=============")
    # print("DNA:", individual_b._dna)
    # print("Fitness:", individual_b.fitness(observations))

    # child_a, child_b = individual_a.crossover(individual_b)
    # mutated_parent_a = individual_a.mutate()

    # print("\nChild A")
    # print("=============")
    # print("DNA:", child_a._dna)
    # print("Fitness:", child_a.fitness(observations))

    # print("\nChild B")
    # print("=============")
    # print("DNA:", child_b._dna)
    # print("Fitness:", child_b.fitness(observations))

    # print("\nMutated parent A")
    # print("=============")
    # print("DNA:", mutated_parent_a._dna)
    # print("Fitness:", mutated_parent_a.fitness(observations))

    # schedule, unable_to_be_placed_observations = child_a.build_schedule(observations)
    # print("Schedule:")
    # print(schedule)
    # print("Unable to be placed observations:")
    # print(unable_to_be_placed_observations)
    # visualize_schedule(date, schedule, child_a._schedule_slot_duration_s, child_a._slots_per_day, "child_a_ObsList1737538994939_schedule.png")

    # ====================
    # Test with known DNA
    # ====================
    dna_to_use = [5, 4, 0, 5, 4, 2, 4, 2, 0, 5, 6, 4, 4, 5, 0, 0, 4, 1, 4, 2, 3, 0, 0, 0, 0, 3, 0, 0, 3, 0]
    test_individual = Individual(len(dna_to_use)//2, day_time_interval_tree, sunrise_sunset_interval_tree, 64)

    possible_to_place_observations, impossible_to_place_observations = filter_out_impossible_to_place_obs(
        observations,
        test_individual._empty_schedule(),
        test_individual._slots_per_day,
        test_individual._schedule_slot_duration_s,
        test_individual._day_time_interval_tree,
        test_individual._sunrise_sunset_interval_tree,
        test_individual._antenna_available
    )

    schedule, unable_to_be_placed_observations = test_individual.build_schedule(possible_to_place_observations)
    print("Schedule:")
    print(schedule)
    print("Unable to be placed observations:")
    print(len(unable_to_be_placed_observations), ":", unable_to_be_placed_observations)
    print("Fitness:", test_individual.fitness(observations))
    visualize_schedule(
        date,
        impossible_to_place_observations,
        unable_to_be_placed_observations,
        schedule,
        test_individual._fitness,
        test_individual._schedule_slot_duration_s,
        test_individual._slots_per_day,
        "test_individual_ObsList1737538994939_schedule.png"
    )
