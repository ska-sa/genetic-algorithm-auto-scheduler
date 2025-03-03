import random

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
            self.schedules.append([timeslot.id, (random.choice(PROPOSALS).id if random.random() < 0.75 else None)])
        return

    def get_proposal_timeslot_indexes(self, proposal_id: int) -> list[int]:
        timeslot_indexes: list[int] = []
        for i, schedule in enumerate(self.schedules):
            if schedule[1] == proposal_id:
                timeslot_indexes.append(i)
        return timeslot_indexes

    # Contraints
    #   

    def compute_penalty(self, proposal_id) -> float:
        penalty: float = 1
        for schedule in self.schedules:
            t_id, p_id = schedule
            if p_id is not None and p_id == proposal_id:
                timeslot = get_timeslot_by_id(t_id)
                proposal = get_proposal_by_id(p_id)
                proposal_timeslot_indexes = self.get_proposal_timeslot_indexes(proposal_id)
                penalty *= (0.1 ** (abs(proposal.simulated_duration - timeslot.get_duration() * len(proposal_timeslot_indexes)) / (7 * 24 * 60 * 60))) # Apply penalty for partially allocated proposal
                penalty *= (0.9 ** ((1 - (min(proposal_timeslot_indexes) + len(proposal_timeslot_indexes) - max(proposal_timeslot_indexes))) / (7 * 24 * 60 * 60))) # Apply penalty for gaps of a partially allocated proposal
        return penalty
    
    def score(self):
        score: float = 0.0
        #total_duration: float = 0.0
        for schedule in self.schedules:
            timeslot_id, proposal_id = schedule
            if proposal_id:
                proposal = get_proposal_by_id(proposal_id)
                #timeslot = get_timeslot_by_id(timeslot_id)
                score += proposal.score * self.compute_penalty(proposal_id)
        return score #/ total_duration

    
    def crossover(self, schedules: list[list[int]]) -> list[list[int]]:
        offspring_schedules: list[list[int]] = list()
        for schedule_1, schedule_2 in zip(self.schedules, schedules):
            offspring_schedules.append(schedule_1 if random.random() > 0.5 else schedule_2)
        return offspring_schedules
    
    def mutation(self, mutation_rate=0.3) -> None:
        mutation_indexes: list[int] = []
        while len(mutation_indexes) != int(mutation_rate * len(self.schedules)):
            mutation_index = random.randint(0, len(self.schedules) - 1)
            if mutation_index not in mutation_indexes:
                mutation_indexes.append(mutation_index)
            
        for mutation_index in mutation_indexes:
            self.schedules[mutation_index][1] = random.choice(PROPOSALS).id if random.random() > 0.75 else None
    
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
                is_first_block: bool = False
                # Check if proposal doesn't exist in our unique proposals list
                if proposal.id not in unique_proposals:
                    is_first_block = True
                    unique_proposals.append(proposal.id)

                # Calculate the position of the proposal on the grid
                weekday = timeslot.start_time.weekday()
                time_index = timeslot.start_time.hour

                # Determine the color based on the proposal ID
                color = f'C{proposal.id % 10}'

                # Add a rectangle for the proposal
                rect = matplotlib.patches.Rectangle(((weekday + 1) % 7, time_index), 1, 1, facecolor=color, alpha=0.5, edgecolor='black', linewidth=2)
                ax.add_patch(rect)

                if is_first_block:
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
        plt.savefig(f"output/timetable_{datetime.now()}.png")

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