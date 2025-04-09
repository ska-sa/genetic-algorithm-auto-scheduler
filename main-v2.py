import random
import matplotlib
import csv
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, date, time, timedelta
from classes.timeslot import Timeslot
from classes.proposal import Proposal
import copy

PROPOSALS: list[Proposal] = list()
MIN_DATE: date = date.today()
MAX_DATE: date = date.today()

def read_proposals_from_csv(file_path: str) -> list[Proposal]:
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
                int(row['id']),
                row['owner_email'],
                30 * 60,
                prefered_dates_start,
                prefered_dates_end,
                avoid_dates_start,
                avoid_dates_end,
                True if str(row['night_obs']).lower() == "yes" else False,
                True if str(row['avoid_sunrise_sunset']).lower == "yes" else False,
                int(row['minimum_antennas']),
                Proposal.parse_time(row['lst_start']),
                Proposal.parse_time(row['lst_start_end']),
                int(row['simulated_duration']),
                get_score(str(row['proposal_id']))
            ))
                
    
    return proposals

def get_score(proposal_id: str):
    return random.randint(1, 4) # In future we have to classify proposals to get their actual rates

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



def get_proposal_by_id(proposal_id: int) -> Proposal:
    global PROPOSALS
    return next((p for p in PROPOSALS if p.id == proposal_id), None)


def lst_to_utc(date: date, lst_time: time) -> datetime:
    return datetime.combine(date, lst_time)

def get_night_window(date: date) -> tuple[datetime, datetime]:
    """
    Return night datetime window for that day in Cape Town.
    
    Parameters:
    date (date): The date for which to calculate the night window.
    
    Returns:
    tuple[datetime, datetime]: Start and end datetime of the night window.
    """
    # Start of the night at 18:00 (6 PM)
    start_datetime = datetime(date.year, date.month, date.day, 18, 0, 0)
    
    # End of the night at 06:00 (6 AM) the next day
    end_datetime = start_datetime + timedelta(hours=12)  # 18:00 to 06:00 next day

    return (start_datetime, end_datetime)

def get_sunrise_sunset(date: date) -> tuple[datetime, datetime]:
    """
    Return sunrise and sunset datetime for that day in Cape Town.
    
    Parameters:
    date (date): The date for which to calculate sunrise and sunset.
    
    Returns:
    tuple[datetime, datetime]: Sunrise and sunset datetime objects.
    """
    # Set average sunrise and sunset times
    sunrise_datetime = datetime(date.year, date.month, date.day, 6, 0, 0)  # 6:00 AM
    sunset_datetime = datetime(date.year, date.month, date.day, 18, 0, 0)  # 6:00 PM
    return sunrise_datetime, sunset_datetime

# Checkout astropy to check lst start window, night window, and sunrise and sunset
class Timetable:
    def __init__(self, schedules: list[list[int]] = None):
        if schedules is None:
            self.schedules = list()
            self.generate()
        else:
            self.schedules = schedules

    def all_constraints_met(self, proposal: Proposal, start_datetime: datetime) -> bool:
        return self.night_obs_contraint_met(proposal, start_datetime) and self.avoid_sunrise_sunset_contraint_met(proposal, start_datetime)
    
    def night_obs_contraint_met(self, proposal: Proposal, start_datetime: datetime) -> bool:
        if proposal.night_obs:
            # Compute end datetime based on simulated duration
            end_datetime = start_datetime + timedelta(minutes=proposal.simulated_duration)
            night_start_datetime, night_end_datetime = get_night_window(start_datetime.date())

            # Check if both start and end datetimes are outside the night window
            if (start_datetime < night_start_datetime and end_datetime < night_start_datetime) or \
               (start_datetime > night_end_datetime and end_datetime > night_end_datetime):
                return True  # Constraint met
            return False  # Constraint not met
        return True  # If night observations are not required, constraint is met
    
    def avoid_sunrise_sunset_contraint_met(self, proposal: Proposal, start_datetime: datetime) -> bool:
        if proposal.avoid_sunrise_sunset:
            # Get sunrise and sunset datetimes
            sunrise_datetime, sunset_datetime = get_sunrise_sunset(date=start_datetime.date())

            # Compute end datetime based on the proposal's duration
            end_datetime = start_datetime + timedelta(minutes=proposal.simulated_duration)

            # Check if sunrise or sunset occurs within the proposal's duration
            if (sunrise_datetime >= end_datetime) or (sunset_datetime <= start_datetime):
                return True  # Constraint met (neither occurs during the proposal)
            return False  # Constraint not met (one of them occurs during the proposal)
        return True  # If avoiding sunrise/sunset is not required, constraint is met

    def generate_datetime(self, proposal_id: int) -> datetime:
        proposal: Proposal = get_proposal_by_id(proposal_id)
        
        for _ in range(10):  # Retry up to 10 times
            # Randomly generate a date between MIN_DATE and MAX_DATE
            randomly_generated_date = self.random_date(MIN_DATE, MAX_DATE)
            
            # Skip if the date exceeds MAX_DATE
            if randomly_generated_date > MAX_DATE:
                continue

            # Randomly generate a time between lst_start_time and lst_end_time
            randomly_generated_time = self.random_time(proposal.lst_start_time, proposal.lst_start_end_time)

            # Combine date and time to get the start datetime
            start_datetime = datetime.combine(randomly_generated_date, randomly_generated_time)
            end_datetime = start_datetime + timedelta(seconds=proposal.simulated_duration)
            #if start_datetime.weekday() == 3 or end_datetime.weekday() == 3: # Skip Wednsday
            #    continue

            # Check if all constraints are met
            if self.all_constraints_met(proposal, start_datetime):
                return start_datetime
        
        return None  # Return None if no valid datetime is found after retries

    def random_date(self, min_date: date, max_date: date) -> date:
        delta = max_date - min_date
        random_days = random.randint(0, delta.days)
        return min_date + timedelta(days=random_days)

    def random_time(self, start_time: time, end_time: time) -> time:
        # Convert start and end time to total seconds
        start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
        end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second

        # If the end time is less than the start time, it means it wraps to the next day
        if end_seconds < start_seconds:
            end_seconds += 24 * 3600  # Add 24 hours in seconds to end_time

        # Generate a random time in seconds between start and end
        random_seconds = random.randint(start_seconds, end_seconds)

        # Convert back to hours, minutes, seconds
        hours, remainder = divmod(random_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return time(hour=hours % 24, minute=minutes, second=seconds)  # Ensure hours are within 24

    def generate(self) -> None:
        global PROPOSALS
        
        for proposal in PROPOSALS:
            start_datetime = self.generate_datetime(proposal.id) if random.random() > 0.75 else None
            self.schedules.append([proposal.id, start_datetime])  # Append as a list
        
    
    def compute_score(self) -> float:
        global PROPOSALS
        total_clash_time: float = 0
        total_time: float = 0

        for schedule in self.schedules:
            proposal_id, start_datetime = schedule
            if start_datetime is not None:
                proposal: Proposal = get_proposal_by_id(proposal_id)
                
                
                for another_proposal_id, another_proposal_start_datetime in self.schedules:
                    another_proposal: Proposal = get_proposal_by_id(another_proposal_id)
                    
                    if (
                        proposal_id != another_proposal_id and
                        another_proposal_start_datetime is not None
                    ):
                        # Calculate end times for both proposals
                        proposal_end_datetime = start_datetime + timedelta(seconds=proposal.simulated_duration)
                        another_proposal_end_datetime = another_proposal_start_datetime + timedelta(seconds=another_proposal.simulated_duration)

                        # Check for clash
                        # Calculate clash time
                        max_start = max(start_datetime, another_proposal_start_datetime)
                        min_end = min(proposal_end_datetime, another_proposal_end_datetime)
                        
                        # Calculate clash time in seconds
                        clash_time = max(0, (min_end - max_start).total_seconds())
                        total_clash_time += clash_time

                        total_time += proposal.simulated_duration

        total_num_proposals = len(self.schedules)
        total_num_unscheduled_proposals = [start_datetime for _, start_datetime in self.schedules].count(None)

        # Simplified check for zero division
        if total_time == 0 or total_num_proposals == 0:
            return 0.0

        numerator = 0
        denominator = 1

        total_non_clash_time = total_time - total_clash_time
        total_num_scheduled_proposals = total_num_proposals - total_num_unscheduled_proposals
        if total_time > total_num_proposals:
            scaler = total_time / total_num_proposals
            numerator = total_non_clash_time * 0.9 + scaler * total_num_scheduled_proposals * 0.1
            denominator = total_time * 0.9 + scaler * total_num_proposals * 0.1
        else:
            scaler = total_num_proposals / total_time
            numerator = scaler * total_non_clash_time * 0.9 + total_num_scheduled_proposals * 0.1
            denominator = scaler * total_time * 0.9 + total_num_proposals * 0.1

        score = numerator / denominator
        # Calculate score
        #score = ((total_time - total_clash_time) * (total_num_proposals - total_num_unscheduled_proposals) * 1.0) / (total_time * total_num_proposals * 1.0)
        #score = ((total_time - total_clash_time) / (total_time))  * (0.9) ** ((total_num_proposals) / (total_num_proposals - total_num_unscheduled_proposals))
        
        # Ensure score is non-negative
        return max(0.0, score)

            
    def crossover(self, schedules: list[list[int]]) -> list[list[int]]:
        offspring_schedules: list[list[int]] = list()
        for schedule_1, schedule_2 in zip(self.schedules, schedules):
            offspring_schedules.append(schedule_1 if random.random() > 0.5 else schedule_2)
        return offspring_schedules
    
    def mutation(self, mutation_rate=0.3) -> None:
        global PROPOSALS
        num_of_mutable_schedules: int = int(len(self.schedules) * mutation_rate)
        mutation_indexes: set[int] = set()  # Use a set for unique mutation indexes

        # Create a deep copy of the schedules to avoid modifying the original
        original_schedules = copy.deepcopy(self.schedules)

        while len(mutation_indexes) < num_of_mutable_schedules:
            mutation_index = random.randint(0, len(original_schedules) - 1)
            
            if mutation_index not in mutation_indexes:
                proposal_id = original_schedules[mutation_index][0]  # Get proposal_id
                start_datetime = self.generate_datetime(proposal_id) if random.random() > 0.75 else None  # Compute new start_datetime
                
                # Mutate the copied schedule
                original_schedules[mutation_index][1] = start_datetime  # Mutate the start_datetime at this mutation index
                mutation_indexes.add(mutation_index)

        # Update self.schedules with the mutated schedules
        self.schedules = original_schedules

    
    def remove_clashing_proposals(self) -> None:
        return
    

    def display(self) -> None:
        # Create a figure and axis
        fig, ax = plt.subplots(figsize=(24, 12))

        # Set the x-axis ticks to weekdays
        weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        ax.set_xticks(np.arange(len(weekdays)) + 0.5)
        ax.set_xticklabels(weekdays, ha='center')
        ax.set_xlim(-0.5, len(weekdays) + 0.5)  # Ensure the last block is aligned

        # Determine the time range for the y-axis
        start_time = min(schedule[1] for schedule in self.schedules if schedule[1] is not None).replace(hour=0, minute=0)
        end_time = max(schedule[1] + timedelta(seconds=get_proposal_by_id(schedule[0]).simulated_duration) 
                    for schedule in self.schedules if schedule[1] is not None)
        time_range = [start_time + timedelta(hours=h) for h in range(24)]
        ax.set_yticks(np.arange(len(time_range)))
        ax.set_yticklabels([t.strftime('%H:%M') for t in time_range])
        ax.set_ylim(0, 23 + 1)

        # Plot the scheduled proposals
        unique_proposals = {}
        for i, (proposal_id, start_datetime) in enumerate(self.schedules):
            if start_datetime is not None:
                proposal = get_proposal_by_id(proposal_id)
                if proposal:
                    # Calculate the position of the proposal on the grid
                    weekday = start_datetime.weekday()
                    time_index = start_datetime.hour

                    # Determine the color based on the proposal ID
                    color = f'C{random.randint(0, 10)}' 

                    # Add a rectangle for the proposal
                    rect = matplotlib.patches.Rectangle((weekday + 1, time_index), 1, 1, facecolor=color, alpha=0.75, edgecolor='black', linewidth=2)
                    ax.add_patch(rect)

                    # Add text for the proposal
                    ax.text(weekday + 1 + 0.5, time_index + 0.5, proposal.owner_email, ha='center', va='center', color='white')

                    # Store unique proposals for legend
                    unique_proposals[proposal_id] = proposal.owner_email

        # Add a legend
        legend_patches = [plt.Rectangle((0, 0), 1, 1, facecolor=f'C{i % 10}', alpha=0.5, edgecolor='black', linewidth=2) for i in unique_proposals.keys()]
        legend_labels = [f'Proposal {pid}' for pid in unique_proposals.keys()]
        ax.legend(legend_patches, legend_labels, loc='upper left', bbox_to_anchor=(1.05, 1))

        # Set the title and axis labels
        ax.set_title('Timetable')
        ax.set_xlabel('Weekday')
        ax.set_ylabel('Time')

        # Display the plot
        #plt.savefig(f"outputs/timetable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

        # Print the textual output
        for proposal_id, start_datetime in self.schedules:
            if start_datetime is not None:
                proposal = get_proposal_by_id(proposal_id)
                end_time = start_datetime + timedelta(seconds=proposal.simulated_duration)
                if start_datetime.hour == 0:
                    print("--------------------------------")
                    print(f"{start_datetime.strftime('%d %B %Y')}")
                print(f"\t{start_datetime.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\t", end="")
                if proposal:
                    print(proposal.owner_email, proposal.simulated_duration // (60 * 60))
                else:
                    print("")
            else:
                print(f"Proposal ID {proposal_id} is not scheduled.")

        print(f"Fitness: {self.compute_score():.2f}\n")

    def plot(self, filename='weekly_timetable.png'):
        # Define days of the week and colors
        days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        colors = ['gray', 'yellow', 'blue', 'red', 'green', 'brown', 'pink', 
                  'lightgreen', 'lightblue', 'wheat', 'salmon', 'lightcoral', 'lightyellow']

        # Create a figure for plotting
        fig, ax = plt.subplots(figsize=(12, 8))

        # Dictionary to hold color legend
        legend_dict = {}

        # Total number of proposals
        total_proposals = len(self.schedules)
        scheduled_proposals = 0

        # Iterate through schedules to plot each proposal
        for idx, (proposal_id, start_datetime) in enumerate(self.schedules):
            if start_datetime is not None:
                scheduled_proposals += 1  # Count scheduled proposals
                proposal: Proposal = get_proposal_by_id(proposal_id)
                end_datetime = start_datetime + timedelta(seconds=proposal.simulated_duration)

                # Calculate the day of the week and time for plotting
                day_index = start_datetime.weekday()  # Monday is 0 and Sunday is 6
                start_time = start_datetime.hour + start_datetime.minute / 60.0
                end_time = end_datetime.hour + end_datetime.minute / 60.0 

                # Randomly select a color for the block
                color = colors[idx % len(colors)]

                # Handle overnight events
                if (end_time - start_time) < 0:
                    # Draw the first rectangle for the current day
                    ax.fill_between([day_index - 0.5, day_index + 0.5], [start_time, start_time], [24, 24],
                                    color=color, edgecolor='black', linewidth=0.5, alpha=0.25)
                    # Draw the second rectangle for the next day
                    next_day_index = (day_index + 1)  # Wrap around to the start of the week
                    next_start_time = 0  # Start at the bottom of the next day
                    if next_day_index < 7:
                        ax.fill_between([next_day_index - 0.5, next_day_index + 0.5], [next_start_time, next_start_time], [end_time, end_time],
                                        color=color, edgecolor='black', linewidth=0.5, alpha=0.25)

                    # Place index text in the first rectangle
                    ax.text(day_index, (start_time + 24) / 2, str(idx), 
                            ha='center', va='center', fontsize=10, color='black')
                    if next_day_index < 7:
                        # Place index text in the second rectangle
                        ax.text(next_day_index, (next_start_time + end_time) / 2, str(idx), 
                                ha='center', va='center', fontsize=10, color='black')

                else:
                    # Plot the block for the proposal with a black border and 25% opacity
                    ax.fill_between([day_index - 0.5, day_index + 0.5], [start_time, start_time], [end_time, end_time],
                                    color=color, edgecolor='black', linewidth=0.5, alpha=0.25)

                    # Place index text inside the rectangle
                    ax.text(day_index, (start_time + end_time) / 2, str(idx), 
                            ha='center', va='center', fontsize=10, color='black')

                # Add to legend with index and email
                legend_key = f'{idx} {proposal.owner_email} {proposal.lst_start_time.strftime("%H:%M:%S")} {proposal.lst_start_end_time.strftime("%H:%M:%S")} {proposal.night_obs} {proposal.avoid_sunrise_sunset}'
                if legend_key not in legend_dict:
                    legend_dict[legend_key] = color

                print(f"{idx}\t{day_index}\t{start_time:0.2f}\t{end_time:0.2f}\t\t{(end_time - start_time):0.2f}")
     

        # Set the x-axis and y-axis limits and labels
        ax.set_xticks(range(len(days_of_week)))
        ax.set_xticklabels(days_of_week)
        ax.set_xlabel('Days of the Week')
        ax.set_ylabel('Time (hours)')
        ax.set_ylim(0, 24)
        
        # Update the title to include scheduled proposals count
        ax.set_title(f'Weekly Timetable: {scheduled_proposals}/{total_proposals} Proposals', fontsize=16)

        # Add gridlines for better readability
        ax.yaxis.grid(True)

        # Create a legend outside the plot
        handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in legend_dict.values()]
        ax.legend(handles, legend_dict.keys(), title="Proposals", loc='upper left', bbox_to_anchor=(1, 1))

        # Save the plot to a file
        plt.tight_layout()
        plt.savefig(filename, dpi=200)  # Save the figure as a PNG file
        plt.close(fig)  # Close the figure to free up memory



class GeneticAlgorithm():
    def __init__(self, num_of_timetables: int = 5 * 10, num_of_generations: int = 15 * 1000) -> None:
        self.num_of_timetables: int = num_of_timetables
        self.num_of_generations: int = num_of_generations
        self.timetables: list[Timetable] = list()
        self.generate_timetables()

        for generation in range(num_of_generations):
            self.timetables.sort(key=lambda timetable: timetable.compute_score(), reverse=True)
            self.print_fitness(generation)
            self.evolve()
            
    def generate_timetables(self) -> None:
        for _ in range(self.num_of_timetables):
            self.timetables.append(Timetable())
        return

    def evolve(self, crossover_rate: float = 0.2, mutation_rate: float = 0.1) -> None:
        # Elitism: Keep the best timetables
        self.timetables.sort(key=lambda timetable: timetable.compute_score(), reverse=True)
        elite_timetables: list[Timetable] = self.timetables[:int(self.num_of_timetables * 0.75)]
        #print(self.timetables[0].compute_score(), self.timetables[-1].compute_score(), end="\n\n")
        
        
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
        print(self.timetables[0].compute_score())
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
            num_offsprings: int = random.randint(4, 8)
            offsprings: list[Timetable] = list()
            for _ in range(num_offsprings):
                offspring: Timetable = Timetable(parent_timetable_1.crossover(parent_timetable_2.schedules))
                offspring.mutation(mutation_rate=0.2)
                offsprings.append(offspring)
            offsprings.sort(key=lambda timetable: timetable.compute_score(), reverse=True)
            offsprint_timetable: Timetable = random.choice(offsprings[:max(2, int(num_offsprings * 0.4))])
            #offsprint_timetable.mutation()
            self.timetables[index] = offsprint_timetable
            #self.timetables[index].mutation()

        #self.timetables.sort(key=lambda timetable: timetable.score(), reverse=True)
        #self.print_fitness(11)

        #print(self.timetables[0].score(), self.timetables[-1].score(), end="\n\n")
        
        return

    def print_fitness(self, generation: int) -> None:
        # Calculate fitness scores for the first up to 5 timetables
        fitness_scores = [timetable.compute_score() for timetable in self.timetables[:min(5, len(self.timetables))]]
        
        # Sort fitness scores in descending order
        sorted_scores = sorted(fitness_scores, reverse=True)

        # Get the first two fittest and the last two least fittest
        fittest_two = sorted_scores[:2]  # First two (fittest)
        least_fittest_two = sorted_scores[-2:]  # Last two (least fittest)

        # Print the results
        print(f"Generation {generation + 1}:\t", end="")
        print(", ".join(f"{score:3.2f}" for score in fittest_two), end=", ..., ")
        print(", ".join(f"{score:3.2f}" for score in least_fittest_two))



    def get_best_fit_timetable(self) -> Timetable:
        # Sort timetables by score and return the best one
        self.timetables.sort(key=lambda timetable: timetable.compute_score(), reverse=True)
        self.timetables[0].remove_clashing_proposals()
        return self.timetables[0]
    
def can_schedule_proposal(proposal: Proposal) -> bool:
    """Check if a proposal can be scheduled based on its constraints."""
    for day in range((MAX_DATE - MIN_DATE).days + 1):  # Include the last day
        # Get the night window for the current day
        night_start_datetime, night_end_datetime = get_night_window(MIN_DATE + timedelta(days=day))
        sunrise_datetime, sunset_datetime = get_sunrise_sunset(MIN_DATE + timedelta(days=day))

        # Prepare the start times
        min_start_datetime = lst_to_utc(MIN_DATE + timedelta(days=day), proposal.lst_start_time)
        max_start_datetime = lst_to_utc(MIN_DATE + timedelta(days=day), proposal.lst_start_end_time)

        # Check both start times for night observations
        for start_datetime in [min_start_datetime, max_start_datetime]:
            # Check if scheduling within the night window is possible
            if proposal.night_obs:
                if not (start_datetime >= night_start_datetime and 
                        start_datetime + timedelta(seconds=proposal.simulated_duration) <= night_end_datetime):
                    return False  # Constraint not met

            # Check for sunrise/sunset avoidance
            if proposal.avoid_sunrise_sunset:
                if not (start_datetime + timedelta(seconds=proposal.simulated_duration) <= sunrise_datetime or 
                        start_datetime >= sunset_datetime):
                    return False  # Constraint not met

    return True  # All constraints met




def main():
    global PROPOSALS, MIN_DATE, MAX_DATE
    MIN_DATE = date(2025, 2, 9)
    MAX_DATE = date(2025, 2, 15)
    proposals: list[Proposal] = read_proposals_from_csv('./proposals/csv/ProdObsList1743669829782.csv')
    #proposals: list[Proposal] = read_proposals_from_csv('./proposals/csv/ObsList1737538994939.csv')
    random.shuffle(proposals) # Shaffle the proposals

    total_week_duration: int = (MAX_DATE - MIN_DATE - timedelta(days=1)).total_seconds()
    cumulative_week_duration: int = 0
    for proposal in proposals:
        # Check if the proposal can be scheduled
        if not can_schedule_proposal(proposal):
            continue  # Skip this proposal if it cannot be scheduled
        if proposal.night_obs or proposal.avoid_sunrise_sunset:
            print(proposal.owner_email)
        cumulative_week_duration += proposal.simulated_duration
        if cumulative_week_duration > total_week_duration * 0.9:
            break

        # If the proposal is valid, add it to the scheduled proposals
        PROPOSALS.append(proposal)

    """
    print("Desplaying Randomly Generated Timetable...")
    timetable = Timetable()
    timetable.display()

    print("Crossover...")
    parent_timetable_1: Timetable = Timetable()
    parent_timetable_2: Timetable = Timetable()
    print(f"parent_timetable_1 fitnest {parent_timetable_1.compute_score()}\tparent_timetable_2 fitnest {parent_timetable_2.compute_score()}")
    offspring_timetable: Timetable = Timetable(parent_timetable_1.crossover(parent_timetable_2.schedules))
    print(f"offspring_timetable fitness {offspring_timetable.compute_score()}")

    print("Mutation...")
    offspring_timetable.mutation()
    print(f"offspring_timetable fitness after mutation {offspring_timetable.compute_score()}")

    print(f"offspring_timetable fitnest {offspring_timetable.compute_score()}\tparent_timetable_2 fitnest {parent_timetable_2.compute_score()}")
    offspring_timetable_1: Timetable = Timetable(offspring_timetable.crossover(parent_timetable_2.schedules))
    print(f"offspring_timetable_1 fitness {offspring_timetable_1.compute_score()}")
    
    exit()
    """

    print("Generating Timetable using Genetic Algorithim")
    genetic_algorithm: GeneticAlgorithm = GeneticAlgorithm(10, 1000)
    best_timetable: Timetable = genetic_algorithm.get_best_fit_timetable()
    best_timetable.display()
    best_timetable.plot(filename=f'outputs/week {MIN_DATE.strftime("%m-%d-%Y")} to {MAX_DATE.strftime("%m-%d-%Y")} timetable.png')
    
if __name__ == "__main__":
    main()