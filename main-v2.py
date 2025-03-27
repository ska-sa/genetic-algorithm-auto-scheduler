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

def utc_to_lst(utc_datetime: datetime) -> datetime:
    """
    Convert UTC datetime to Local Sidereal Time (LST) datetime.
    
    Parameters:
    utc_datetime (datetime): The UTC datetime object to be converted.
    
    Returns:
    datetime: The corresponding LST datetime object.
    """
    # Get the longitude and latitude of the location (in degrees)
    longitude = 18.478847  # Cape Town longitude
    latitude = -33.944382  # Cape Town latitude

    # Calculate the Sidereal Time at Greenwich (GST) in hours
    gst_hours = (utc_datetime.timetuple().tm_year,
                 utc_datetime.timetuple().tm_yday,
                 utc_datetime.hour + utc_datetime.minute / 60 + utc_datetime.second / 3600)
    gst_hours = (18.697374558 + 24.06570982441908 * (gst_hours[0] - 2000) + 0.000026 * (gst_hours[0] - 2000) ** 2 + 1.0027379093 * gst_hours[1] + gst_hours[2]) % 24

    # Convert GST to LST
    lst_hours = (gst_hours + longitude / 15) % 24

    # Convert LST hours to LST datetime
    lst_datetime = utc_datetime.replace(hour=int(lst_hours),
                                       minute=int((lst_hours % 1) * 60),
                                       second=int((lst_hours % 1) * 3600) % 60,
                                       microsecond=0)

    return lst_datetime


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


class Timetable:
    def __init__(self, schedules: list[list[int]] = None):
        if schedules is None:
            self.schedules = []
            self.generate()
        else:
            self.schedules = schedules

    def generate_datetime(self, proposal_id: int, 
                          min_datetime: datetime = datetime(2025, 2, 9, 0, 0, 0), 
                          max_datetime: datetime = datetime(2025, 2, 15, 23, 59, 59)) -> datetime:
        while True:
            # Generate a random date between min_datetime and max_datetime
            random_timestamp = random.randint(int(min_datetime.timestamp()), int(max_datetime.timestamp()))
            start_datetime = datetime.fromtimestamp(random_timestamp)

            # Check if all constraints are met
            if self.all_constraints_met(proposal_id):
                return start_datetime 

    def generate(self) -> None:
        global PROPOSALS
        
        for proposal in PROPOSALS:
            start_datetime = self.generate_datetime(proposal.id) if random.random > 0.75 else None
            self.schedules.append([proposal.id, start_datetime])  # Append as a list
            

    def all_constraints_met(self, proposal_id: int) -> bool:
        # Placeholder for actual constraint checking logic
        return True  # Replace with actual logic
    
    def compute_score(self) -> float:
        global PROPOSALS
        score: float = 1
        total_clash_time: float = 0
        total_time: float = 0
        for schedule in self.schedules:
            proposal_id, start_datetime = schedule
            if start_datetime is not None:
                proposal: Proposal = get_proposal_by_id(proposal_id=proposal_id)
                total_time += proposal.simulated_duration
                for PROPOSAL in PROPOSALS:
                    if PROPOSAL != proposal and (PROPOSAL.start_datetime - proposal.start_datetime > max(PROPOSAL.simulated_duration, proposal.simulated_duration)):
                        clash_time = None # compute classhig time 
                        total_clash_time += clash_time

        score = total_clash_time / total_time
        return score
            
    def crossover(self, schedules: list[list[int]]) -> list[list[int]]:
        offspring_schedules: list[list[int]] = list()
        for schedule_1, schedule_2 in zip(self.schedules, schedules):
            offspring_schedules.append(schedule_1 if random.random() > 0.5 else schedule_2)
        return offspring_schedules
    
    def mutation(self, mutation_rate=0.2) -> None:
        global PROPOSALS
        num_of_mutable_schedules: int = int(len(self.schedules) * mutation_rate)
        mutation_indexes: list[int] = list()
        while len(mutation_index) < num_of_mutable_schedules:
            mutation_index = random.randint(0, len(self.schedules) -1)
            if mutation_index not in mutation_indexes:
                proposal_id = self.schedules[mutation_index][0] # Get proposal_id
                start_datetime = self.generate_datetime(proposal_id) if random.random > 0.75 else None # Compute new start_datetinme
                self.schedules[mutation_index][1] = start_datetime # Mutate the start_datettime at this mutation index
                mutation_indexes.append(mutation_index)

    

    """
    def all_hard_contraints_met(self, timeslot: Timeslot, proposal: Proposal):
        return self.is_avoid_sunrise_sunset_cosnstraint_met(timeslot, proposal) and self.is_night_obs_contraint_met(timeslot, proposal) and self.is_lst_start_start_end_contraint_met(timeslot, proposal) and self.is_over_schedule_contraint_met(timeslot, proposal)

    def is_avoid_sunrise_sunset_cosnstraint_met(self, timeslot: Timeslot, proposal: Proposal):
        if proposal.avoid_sunrise_sunset:
            sunrise_datetime, sunset_datetime = get_sunrise_sunset(timeslot.start_time.date())
            
            # Create a list of sunrise and sunset datetimes
            sun_events = [sunrise_datetime, sunset_datetime]

            # Check if timeslot overlaps with any sun event
            for event_datetime in sun_events:
                if timeslot.start_time <= event_datetime <= timeslot.end_time:
                    return False
        return True
    
    def is_lst_start_start_end_contraint_met(self, timeslot: Timeslot, proposal: Proposal):
        if len(self.schedules) == len(TIMESLOTS):
            start_time: datetime = utc_to_lst(datetime.combine(timeslot.start_time.date(), proposal.lst_start_time))
            start_end_time: datetime = utc_to_lst(datetime.combine(timeslot.start_time.date(), proposal.lst_start_end_time))
            
            timeslot_start_time: datetime = utc_to_lst(timeslot.start_time)

            timeslot_id = timeslot.id
            proposal_id = proposal.id

            try:
                timeslot_index: int = [schedule[0] for schedule in self.schedules].index(timeslot_id)
                proposal_index: int = [schedule[1] for schedule in self.schedules].index(proposal_id)
            except:
                return True


            if not (start_time <= timeslot_start_time and start_end_time >= timeslot_start_time) and (timeslot_index == proposal_index):
                return False
        return True
    
    def is_night_obs_contraint_met(self, timeslot: Timeslot, proposal: Proposal):
        night_start_datetime, night_end_datetime = get_night_window(timeslot.start_time.date())
        if proposal.night_obs and not (night_start_datetime <= timeslot.start_time <= night_end_datetime):
            return False
        return True
    
    def is_over_schedule_contraint_met(self, timeslot: Timeslot, proposal: Proposal):
        num_of_timeslots: int = [schedule[1] for schedule in self.schedules].count(proposal.id)
        if num_of_timeslots * timeslot.get_duration() >= proposal.simulated_duration:
            return False
        return True



    def compute_penalty(self, proposal_id) -> float:
        global TIME_RESOLUTION
        penalty: float = 1
        penalty_factors: list[float] = list([0.95, 0.90, 0.85, 0.80])
        penalty_factor: float = penalty_factors[0]

        scheduled_time: float = 0.0
        requested_time: float = 0.0
        
        List of contraints
            - 1. Check for proposal score/priority SCI
            - 2. Check LST start - start end window
            - 3. Check for gaps between scheduled proposals
            - 4. Check for partially allocated proposals
            - 5. Check for night obs.
            - 6. Check for avoid sunset/sunrise
            - 7. Check for min antenna *
        
        for schedule in self.schedules:
            t_id, p_id = schedule
            unique_proposal_ids: list[int] = list()
            if p_id is not None and p_id == proposal_id:
                timeslot = get_timeslot_by_id(t_id)
                proposal = get_proposal_by_id(p_id)

                # 1. Check for proposal score/priority
                penalty_factor = penalty_factors[proposal.get_score() - 1]

                # 2. Check LST start - start end window
                start_time: datetime = utc_to_lst(datetime.combine(timeslot.start_time.date(), proposal.lst_start_time))
                start_end_time: datetime = utc_to_lst(datetime.combine(timeslot.start_time.date(), proposal.lst_start_end_time))

                timeslot_start_time: datetime = utc_to_lst(timeslot.start_time)
                if not (start_time <= timeslot_start_time and start_end_time >= timeslot_start_time) and (proposal.id not in unique_proposal_ids):
                    # Calculate the midpoint
                    midpoint_start_time: datetime = start_time + (start_end_time - start_time) / 2
                    
                    #penalty = 0 # For hard contraints
                    penalty *= (penalty_factor * 0.1) ** abs((midpoint_start_time - timeslot_start_time).total_seconds() / TIME_RESOLUTION)
                    

                # 3. Checking gaps between scheduled proposals
                proposal_timeslot_indexes = self.get_proposal_timeslot_indexes(proposal_id)
                if proposal.id not in unique_proposal_ids:
                    penalty *= ((penalty_factor * 0.5) ** (abs((proposal.simulated_duration - timeslot.get_duration() * len(proposal_timeslot_indexes)) / TIME_RESOLUTION))) # Apply penalty for partially allocated proposal
                
                # 4. Checking partially allocated proposals
                penalty *= (penalty_factor ** ((1 - (min(proposal_timeslot_indexes) + len(proposal_timeslot_indexes) - max(proposal_timeslot_indexes))) / TIME_RESOLUTION)) # Apply penalty for gaps of a partially allocated proposal
        

                # 5. Check for night obs.
                night_start_datetime, night_end_datetime = get_night_window(timeslot.start_time.date())

                # Check if the proposal requires night observation and if the timeslot is outside the night window
                if proposal.night_obs and not (night_start_datetime <= timeslot.start_time <= night_end_datetime):
                    # Calculate the midpoint of the night window
                    night_midpoint_datetime = night_start_datetime + (night_end_datetime - night_start_datetime) / 2
                    
                    # Calculate the midpoint of the timeslot
                    timeslot_midpoint_datetime = timeslot.start_time + (timeslot.end_time - timeslot.start_time) / 2
                    
                    # Calculate the penalty based on the difference from the night midpoint
                    penalty *= ((penalty_factor * 0.1) ** abs((timeslot_midpoint_datetime - night_midpoint_datetime).total_seconds() / TIME_RESOLUTION))
                    #penalty = 0 # For hard contraints

                    # 6. Check for avoid sunset/sunrise
                    if proposal.avoid_sunrise_sunset:
                        sunrise_datetime, sunset_datetime = get_sunrise_sunset(timeslot.start_time.date())
                        
                        # Create a list of sunrise and sunset datetimes
                        sun_events = [sunrise_datetime, sunset_datetime]

                        # Check if timeslot overlaps with any sun event
                        for event_datetime in sun_events:
                            if timeslot.start_time <= event_datetime <= timeslot.end_time:
                                # Apply penalty based on the difference between the midpoint and the clashing event
                                #penalty = 0 # For hard contraints
                                penalty *= (penalty_factor * 0.1) ** abs((timeslot_midpoint_datetime - event_datetime).total_seconds() / TIME_RESOLUTION)
                                break  # Exit loop after applying penalty for the first overlapping event



                # 7. Check for min antenna *
                pass

                
                if proposal_id is not None:
                    scheduled_time += timeslot.get_duration()
                if proposal.id not in unique_proposal_ids:
                    requested_time += proposal.simulated_duration
                    unique_proposal_ids.append(proposal.id)
        # 8. Compared scheduled used time with requestsed time
        penalty *= scheduled_time / requested_time
        
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
    
    def mutation(self, mutation_rate=0.2) -> None:
        global PROPOSALS
        num_of_mutable_schedules: int = int(len(self.schedules) * mutation_rate)
        for _ in range(num_of_mutable_schedules):
            mutation_index = random.randint(0, len(self.schedules) - 1)
            proposal_id: int = None
            timeslot_id: int = self.schedules[mutation_index][0]
            if random.random() < 0.75:
                for _ in range(6):
                    proposal: Proposal = random.choice(PROPOSALS)
                    if self.all_hard_contraints_met(get_timeslot_by_id(timeslot_id), proposal):
                        proposal_id = proposal.id
            self.schedules[mutation_index] =  list([timeslot_id, proposal_id])

          
    def remove_partialy_allocated_proposals(self) -> None:
        return
    """
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
            timeslot: Timeslot = get_timeslot_by_id(timeslot_id)
            proposal: Proposal = get_proposal_by_id(proposal_id)
            if proposal:
                # Check if proposal doesn't exist in our unique proposals list
                if proposal.id not in unique_proposals:
                    unique_proposals.append(proposal.id)

                # Calculate the position of the proposal on the grid
                weekday = timeslot.start_time.weekday()
                time_index = timeslot.start_time.hour

                # Determine the color based on the proposal ID
                color = f'C{PROPOSALS.index(proposal)}'

                # Add a rectangle for the proposal
                rect = matplotlib.patches.Rectangle(((weekday + 1) % 7, time_index), 1, 1, facecolor=color, alpha=0.5, edgecolor='black', linewidth=1)
                ax.add_patch(rect)

               
                ax.text((weekday + 1) % 7 + 0.5, time_index + 0.5, proposal.owner_email, ha='center', va='center', color='white')

        # Add a legend
        #legend_patches = [plt.Rectangle((0, 0), 1, 1, facecolor=f'C{i}', alpha=0.5, edgecolor='black', linewidth=2) for i in range(len(unique_proposals))]
        #legend_labels = [f'Proposal {i}' for i in unique_proposals]
        #ax.legend(legend_patches, legend_labels, loc='upper left', bbox_to_anchor=(1.05, 1))

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
                print(proposal.owner_email, proposal.simulated_duration // (60 * 60))
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
            num_offsprings: int = random.randint(4, 8)
            offsprings: list[Timetable] = list()
            for _ in range(num_offsprings):
                offspring: Timetable = Timetable(parent_timetable_1.crossover(parent_timetable_2.schedules))
                offspring.mutation(mutation_rate=0.2)
                offsprings.append(offspring)
            offsprings.sort(key=lambda timetable: timetable.score(), reverse=True)
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
        fitness_scores = [timetable.score() for timetable in self.timetables[:min(5, len(self.timetables))]]
        
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
        self.timetables.sort(key=lambda timetable: timetable.score(), reverse=True)
        self.timetables[0].remove_partialy_allocated_proposals()
        return self.timetables[0]


def main():
    global TIMESLOTS, PROPOSALS
    proposals: list[Proposal] = read_proposals_from_csv('./proposals/csv/ObsList1737538994939.csv')
    total_week_duration: int = 60 * 60 * 24
    cumulative_week_duration: int = 0
    for proposal in proposals:
        cumulative_week_duration += proposal.simulated_duration
        if cumulative_week_duration >= total_week_duration * 2:
            break
        PROPOSALS.append(proposal)
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
    genetic_algorithm: GeneticAlgorithm = GeneticAlgorithm(20, 10000)
    best_timetable: Timetable = genetic_algorithm.get_best_fit_timetable()
    best_timetable.display()

if __name__ == "__main__":
    main()