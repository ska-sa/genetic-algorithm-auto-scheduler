import random
import matplotlib
import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, date, time, timedelta
from classes.timeslot import Timeslot
from classes.proposal import Proposal

TIMESLOTS: list[Timeslot] = list()
PROPOSALS: list[Proposal] = list()

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


            proposals.append(Proposal(
                int(row['id']),
                row['owner_email'],
                30 * 60,
                prefered_dates_start,
                prefered_dates_end,
                avoid_dates_start,
                avoid_dates_end,
                bool(row['night_obs']),
                bool(row['avoid_sunrise_sunset']),
                int(row['minimum_antennas']),
                Proposal.parse_time(row['lst_start']),
                Proposal.parse_time(row['lst_start_end']),
                int(row['simulated_duration']),
                random.randint(1,  1) #float(row['score'])
            ))
    return proposals


def generate_timeslots(start_date: date, end_date: date, timeslot_duration: int = 60 * 60) -> list[Timeslot]:
    timeslots = []
    current_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)
    timeslot_id = 0

    while current_datetime < end_datetime:
        end_time = min(current_datetime + timedelta(seconds=timeslot_duration), end_datetime)
        timeslots.append(Timeslot(timeslot_id, current_datetime, end_time))
        current_datetime = end_time
        timeslot_id += 1

    return timeslots

# Global Variables

#PROPOSALS = [
#    Proposal(20241207210517, "nushikia.chamba@nasa.gov", 60 * 30, [date.fromisoformat("2025-02-15")], [date.fromisoformat("2025-04-01")], [], [], True, True, 58, Proposal.parse_time("7:00"), Proposal.parse_time("8:30"), 21999, 1),
#]

#TIMESLOTS = [
#    Timeslot(0, datetime(2025, 1, 1, 0, 0, 0), datetime(2025, 1, 1, 1, 0, 0))
#]


def get_timeslot_by_id(timeslot_id: int) -> Timeslot:
    global TIMESLOTS
    return next((t for t in TIMESLOTS if t.id == timeslot_id), None)

def get_proposal_by_id(proposal_id: int) -> Proposal:
    global PROPOSALS
    return next((p for p in PROPOSALS if p.id == proposal_id), None)

def uct_to_lst(datetime: datetime) -> datetime:
    """
    Convert uct to lst
    """
    return datetime

def get_night_window(date: date) -> tuple[datetime, datetime]:
    """
    Return night datetime window for that day
    """
    start_datetime: datetime = datetime(date)
    start_datetime.hour = 18
    end_datetime: datetime = datetime(date)
    end_datetime.day += 1
    end_datetime.hour = 6
    return (start_datetime, end_datetime)

def get_sunrise_sunset(date: date) -> tuple[datetime, datetime]:
    """
    Return sunrise and sunset datetime for that day
    """
    sunrise_datetime: datetime = datetime(date)
    sunrise_datetime.hour = 6
    sunset_datetime: datetime = datetime(date)
    sunset_datetime.hour = 18
    return sunrise_datetime, sunset_datetime


class Timetable:
    def __init__(self, schedules: list[list[int]] = list()):
        self.schedules = list()
        if schedules == list():
            self.generate()
        else:
            self.schedules = schedules

    def generate(self) -> None:
        global TIMESLOTS, PROPOSALS
        for timeslot in TIMESLOTS:
            self.schedules.append(
                [timeslot.id, (random.choice(PROPOSALS).id if random.random() > 0.25 else None)]
            )
        return

    def get_proposal_timeslot_indexes(self, proposal_id: int) -> list[int]:
        timeslot_indexes: list[int] = []
        for i, schedule in enumerate(self.schedules):
            if schedule[1] == proposal_id:
                timeslot_indexes.append(i)
        return timeslot_indexes

    def compute_penalty(self, proposal_id) -> float:
        penalty: float = 1
        penalty_factors: list[float] = list([0.95, 0.90, 0.85, 0.80])
        penalty_factor: float = penalty_factors[0]
        """
        List of contraints
            - 1. Check for proposal score/priority
            - 2. Check LST start - start end window
            - 3. Check for gaps between scheduled proposals
            - 4. Check for partially allocated proposals
            - 5. Check for night obs.
            - 6. Check for avoid sunset/sunrise
            - 7. Check for min antenna *
        """
        for schedule in self.schedules:
            t_id, p_id = schedule
            if p_id is not None and p_id == proposal_id:
                timeslot = get_timeslot_by_id(t_id)
                proposal = get_proposal_by_id(p_id)

                # 1. Check for proposal score/priority
                penalty_factor = penalty_factors[proposal.get_score() - 1]

                # 2. Check LST start - start end window
                start_time: time = uct_to_lst(timeslot.start_time)
                start_end_time: time = uct_to_lst(timeslot.start_time)
                timeslot_start_time: time = time(timeslot.start_time)
                if not (start_time <= timeslot_start_time and start_end_time >= timeslot_start_time):
                    midpoint_start_time: time = (start_time + start_end_time) / 2
                    penalty * (penalty_factor ** abs(midpoint_start_time - timeslot_start_time))

                # 3. Checking gaps between scheduled proposals
                proposal_timeslot_indexes = self.get_proposal_timeslot_indexes(proposal_id)
                penalty *= (penalty_factor ** (abs(proposal.simulated_duration - timeslot.get_duration() * len(proposal_timeslot_indexes)) / (7 * 24 * 60 * 60))) # Apply penalty for partially allocated proposal
                
                # 4. Checking partially allocated proposals
                penalty *= (penalty_factor ** ((1 - (min(proposal_timeslot_indexes) + len(proposal_timeslot_indexes) - max(proposal_timeslot_indexes))) / (7 * 24 * 60 * 60))) # Apply penalty for gaps of a partially allocated proposal
        

                # 5. Check for night obs.
                night_start_datetime, night_end_datetime = get_night_window(date(timeslot.start_time))
                if not (night_start_datetime <= timeslot.start_time and night_end_datetime >= timeslot.end_time):
                    night_mindpoint_datetime = (night_start_datetime + night_end_datetime) / 2
                    timeslot_midpoint_datetime = (timeslot.start_time + timeslot.end_time) / 2
                    penalty *= (penalty_factor ** abs(timeslot_midpoint_datetime - night_mindpoint_datetime))

                # 6. Check for avoid sunset/sunrise
                if proposal.avoid_sunrise_sunset:
                    sunrise_datetime, sunset_datetime = get_sunrise_sunset(date(timeslot.start_time))
                    if (timeslot.start_time <= sunrise_datetime and timeslot.end_time >= sunrise_datetime) or (timeslot.start_time <= sunset_datetime and timeslot.end_time >= sunset_datetime):
                        penalty *= penalty_factor


                # 7. Check for min antenna *
                pass

        return penalty
    
    def score(self):
        score: float = 0.0
        #total_duration: float = 0.0
        for schedule in self.schedules:
            timeslot_id, proposal_id = schedule
            if proposal_id is not None:
                proposal = get_proposal_by_id(proposal_id)
                #timeslot = get_timeslot_by_id(timeslot_id)
                #score += proposal.score * self.compute_penalty(proposal_id)
                score += self.compute_penalty(proposal_id)
        return score #/ total_duration

    
    def crossover(self, schedules: list[list[int]]) -> list[list[int]]:
        offspring_schedules: list[list[int]] = list()
        for schedule_1, schedule_2 in zip(self.schedules, schedules):
            offspring_schedules.append(schedule_1 if random.random() > 0.5 else schedule_2)
        return offspring_schedules
    
    def mutation(self, mutation_rate=0.1) -> None:
        global PROPOSALS
        num_of_mutable_schedules: int = int(len(self.schedules) * mutation_rate)
        for _ in range(num_of_mutable_schedules):
            mutation_index = random.randint(0, len(self.schedules) - 1)
            self.schedules[mutation_index] =  list([self.schedules[mutation_index][0], random.choice(PROPOSALS).id if random.random() > 0.25 else None])

          
    def remove_partialy_allocated_proposals(self) -> None:
        return
    
    def display(self) -> None:
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(24, 12))

        # Set the x-axis ticks to weekdays
        weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        ax.set_xticks(np.arange(len(weekdays)) + 0.5)
        ax.set_xticklabels(weekdays, ha='center')
        ax.set_xlim(-0.5, len(weekdays) + 0.5)  # Add this line to ensure the last block is aligned

        # Set the y-axis ticks to timeslots
        start_time = min(get_timeslot_by_id(timeslot_id).start_time for timeslot_id, _ in self.schedules)
        end_time = max(get_timeslot_by_id(timeslot_id).end_time for timeslot_id, _ in self.schedules)
        time_range = [start_time.replace(hour=h, minute=0) for h in range(24)]
        ax.set_yticks(np.arange(len(time_range)))
        ax.set_yticklabels([t.strftime('%H:%M') for t in time_range])
        ax.set_ylim(0, 23 + 1)

        # Plot the scheduled proposals
        owner_colors = {}
        unique_proposals = []
        for i, (timeslot_id, proposal_id) in enumerate(self.schedules):
            timeslot = get_timeslot_by_id(timeslot_id)
            proposal = get_proposal_by_id(proposal_id)
            if proposal:
                # Check if proposal doesn't exist in our unique proposals list
                if proposal.id not in unique_proposals:
                    unique_proposals.append(proposal.id)

                # Calculate the position of the proposal on the grid
                weekday = timeslot.start_time.weekday()
                time_index = timeslot.start_time.hour

                # Determine the color based on the proposal ID
                color = f'C{proposal.id % 10}'

                # Add a rectangle for the proposal
                rect = matplotlib.patches.Rectangle(((weekday + 1) % 7, time_index), 1, 1, facecolor=color, alpha=0.5, edgecolor='black', linewidth=2)
                ax.add_patch(rect)

               
                ax.text((weekday + 1) % 7 + 0.5, time_index + 0.5, str(proposal.owner_email), ha='center', va='center', color='white')

        # Add a legend
        legend_patches = [plt.Rectangle((0, 0), 1, 1, facecolor=f'C{i}', alpha=0.5, edgecolor='black', linewidth=2) for i in range(len(unique_proposals))]
        legend_labels = [f'Proposal {i}' for i in unique_proposals]
        ax.legend(legend_patches, legend_labels, loc='upper left', bbox_to_anchor=(1.05, 1))

        # Set the title and axis labels
        ax.set_title('Timetable')
        ax.set_xlabel('Weekday')
        ax.set_ylabel('Time')

        # Display the plot
        plt.savefig(f"outputs/timetable_{datetime.now()}.png")

        # Print the textual output
        for timeslot_id, proposal_id in self.schedules:
            timeslot = get_timeslot_by_id(timeslot_id)
            proposal = get_proposal_by_id(proposal_id)
            if timeslot.start_time.hour == 0:
                print("--------------------------------")
                print(f"{timeslot.start_time.strftime('%d %B %Y')}")
            print(f"\t{timeslot.start_time.strftime('%H:%M')} - {timeslot.end_time.strftime('%H:%M')}\t", end="")
            if proposal:
                print(proposal.owner_email, proposal.simulated_duration)
            else:
                print("")

        print(f"Fitness: {self.score():.2f}\n")


class GeneticAlgorithm():
    def __init__(self, num_of_timetables: int = 5 * 10, num_of_generations: int = 15 * 1000) -> None:
        self.num_of_timetables: int = num_of_timetables
        self.num_of_generations: int = num_of_generations
        self.timetables: list[Timetable] = list()
        self.generate_timetables()

        for generation in range(num_of_generations):
            self.timetables.sort(key=lambda timetable: timetable.score(), reverse=True)
            self.print_fitness(generation)
            self.evolve()
            
    def generate_timetables(self) -> None:
        for _ in range(self.num_of_timetables):
            self.timetables.append(Timetable())
        return

    def evolve(self, crossover_rate: float = 0.2, mutation_rate: float = 0.1) -> None:
        # Elitism: Keep the best timetables
        self.timetables.sort(key=lambda timetable: timetable.score(), reverse=True)
        elite_timetables: list[Timetable] = self.timetables[:int(self.num_of_timetables * 0.75)]
        #print(self.timetables[0].score(), self.timetables[-1].score(), end="\n\n")
        
        
        """
        # Crossover: Create new timetables by crossing over the best timetables
        new_timetables: list[Timetable] = list()
        for _ in range(int(self.num_of_timetables * (1 - crossover_rate))):
            parent_timetable_1: Timetable = random.choice(elite_timetables)
            parent_timetable_2: Timetable = random.choice(elite_timetables)
            offspring: Timetable = Timetable(parent_timetable_1.crossover(parent_timetable_2.schedules))
            offspring.mutation()
            new_timetables.append(offspring)

        self.timetables.clear()
        self.timetables.append(elite_timetables[0])
        print(self.timetables[0].score())
        # Replace the old population with the new one
        for timetable in new_timetables:
            self.timetables.append(timetable)
        
        
        while len(self.timetables) != self.num_of_timetables:
            self.timetables.append(random.choice(elite_timetables))
        """
        

        starting_index: int = self.num_of_timetables - 1 - int(self.num_of_timetables * crossover_rate)
        #print(starting_index, self.num_of_timetables, 1)
        for index in range(starting_index, self.num_of_timetables, 1):
            parent_timetable_1: Timetable = random.choice(elite_timetables)
            parent_timetable_2: Timetable = random.choice(elite_timetables)
            #self.timetables[index] = None
            offsprint_timetable: Timetable = Timetable(parent_timetable_1.crossover(parent_timetable_2.schedules))
            offsprint_timetable.mutation()
            self.timetables[index] = offsprint_timetable
            #self.timetables[index].mutation()

        #self.timetables.sort(key=lambda timetable: timetable.score(), reverse=True)
        #self.print_fitness(11)

        #print(self.timetables[0].score(), self.timetables[-1].score(), end="\n\n")
        
        return

    def print_fitness(self, generation: int) -> None:
        fitness_scores = [timetable.score() for timetable in self.timetables[:min(5, len(self.timetables))]]
        print(f"Generation {generation + 1}:\t", end="")
        print(", ".join(f"{score:3.2f}" for score in fitness_scores))

    def get_best_fit_timetable(self) -> Timetable:
        # Sort timetables by score and return the best one
        self.timetables.sort(key=lambda timetable: timetable.score(), reverse=True)
        self.timetables[0].remove_partialy_allocated_proposals()
        return self.timetables[0]


def main():
    global TIMESLOTS, PROPOSALS
    PROPOSALS = read_proposals_from_csv('./proposals/csv/ObsList1737538994939.csv')
    TIMESLOTS = generate_timeslots(date.fromisoformat("2025-02-09"), date.fromisoformat("2025-02-15"))

    """
    print("Desplaying Randomly Generated Timetable...")
    timetable = Timetable()
    timetable.display()

    print("Crossover...")
    parent_timetable_1: Timetable = Timetable()
    parent_timetable_2: Timetable = Timetable()
    print(f"parent_timetable_1 fitnest {parent_timetable_1.score()}\tparent_timetable_2 fitnest {parent_timetable_2.score()}")
    offspring_timetable: Timetable = Timetable(parent_timetable_1.crossover(parent_timetable_2.schedules))
    print(f"offspring_timetable fitness {offspring_timetable.score()}")

    print("Mutation...")
    offspring_timetable.mutation()
    print(f"offspring_timetable fitness after mutation {offspring_timetable.score()}")

    print(f"offspring_timetable fitnest {offspring_timetable.score()}\tparent_timetable_2 fitnest {parent_timetable_2.score()}")
    offspring_timetable_1: Timetable = Timetable(offspring_timetable.crossover(parent_timetable_2.schedules))
    print(f"offspring_timetable_1 fitness {offspring_timetable_1.score()}")
    
    exit()
    """

    print("Generating Timetable using Genetic Algorithim")
    genetic_algorithm: GeneticAlgorithm = GeneticAlgorithm(10, 1000)
    best_timetable: Timetable = genetic_algorithm.get_best_fit_timetable()
    best_timetable.display()

if __name__ == "__main__":
    main()