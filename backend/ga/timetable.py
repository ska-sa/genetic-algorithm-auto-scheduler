import random
from datetime import timedelta, date
from matplotlib import pyplot as plt
from .proposal import Proposal
from .individual import Individual
from .utils import get_global_vars

START_DATE: date = date.today()
END_DATE: date = date.today()
PROPOSALS: list[Proposal] = []

class Timetable(Individual):
    """
    The Timetable class represents a schedule of proposals.
    """
    def __init__(self, schedules: list[Proposal] = []):
        """
        Initialize the Timetable object.

        Args:
            schedules (list[Proposal], optional): A list of Proposal objects to be included in the timetable. Defaults to an empty list.

        Returns:
            None
        """
        global START_DATE, END_DATE, PROPOSALS
        START_DATE, END_DATE, proposals_dict = get_global_vars()
        PROPOSALS = [Proposal.from_dict(p) for p in proposals_dict]
        super(Timetable, self).__init__(schedules)
    
    def remove_clashes(self) -> None:
        """
        Removes any clashing proposals from the timetable using the scheduled_start_datetime and simulated_duration attributes of each proposal in the timetable's schedules list. If any two proposals have overlapping time slots, one of them is randomly removed from the timetable.

        Args:
            None

        Returns:
            None
        """
        schedules: list[Proposal] = self.schedules.copy()  # Create a copy to avoid modifying the original list during iteration
        for i in range(len(schedules)):
            proposal_i: Proposal = schedules[i]
            if proposal_i.scheduled_start_datetime is None:
                continue
            for j in range(i + 1, len(schedules)):
                proposal_j: Proposal = schedules[j]
                if proposal_j.scheduled_start_datetime is None:
                    continue
                
                # Check if the proposals have overlapping time slots
                if (proposal_i.scheduled_start_datetime <= proposal_j.scheduled_start_datetime < proposal_i.scheduled_start_datetime + timedelta(seconds=proposal_i.simulated_duration)) or \
                (proposal_j.scheduled_start_datetime <= proposal_i.scheduled_start_datetime < proposal_j.scheduled_start_datetime + timedelta(seconds=proposal_j.simulated_duration)):
                    # Randomly remove one of the clashing proposals
                    
                    if random.random() < 0.5:
                        schedules.pop(j)
                    else:
                        schedules.pop(i)
        
        self.schedules = schedules  # Update the schedules list with the modified version
    

    def plot(self):
        global START_DATE, END_DATE, PROPOSALS
        # Define days of the week and colors
        days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        colors = ['gray', 'yellow', 'blue', 'red', 'green', 'brown', 'pink', 
                'lightgreen', 'lightblue', 'wheat', 'salmon', 'lightcoral', 'lightyellow']

        # Calculate the number of weeks between the start and end dates
        num_weeks = (END_DATE - START_DATE).days // 7 + 1

        # Get total number of schduled proposals
        total_scheduled_proposals = sum(1 for schedule in self.schedules if schedule.scheduled_start_datetime is not None)

        for week_num in range(num_weeks):
            # Calculate the start and end dates of the current week
            week_start_date = START_DATE + timedelta(days=week_num * 7)
            week_end_date = week_start_date + timedelta(days=6)

            # Create a figure for plotting
            fig, ax = plt.subplots(figsize=(12, 8))

            # Dictionary to hold color legend
            legend_dict = {}

            # Total number of proposals
            total_proposals = len(self.schedules)
            scheduled_proposals = 0

            # Iterate through schedules to plot each proposal
            for idx, proposal in enumerate(self.schedules):
                if proposal.scheduled_start_datetime is not None and week_start_date <= proposal.scheduled_start_datetime.date() <= week_end_date:
                    scheduled_proposals += 1  # Count scheduled proposals
                    end_datetime = proposal.scheduled_start_datetime + timedelta(seconds=proposal.simulated_duration)

                    # Calculate the day of the week and time for plotting
                    day_index = proposal.scheduled_start_datetime.weekday()  # Monday is 0 and Sunday is 6
                    start_time = proposal.scheduled_start_datetime.hour + proposal.scheduled_start_datetime.minute / 60.0
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
                    legend_key = f'{idx} {proposal.owner_email.split("@")[0].split(".")[0]} {proposal.lst_start_time.strftime("%H:%M:%S")} {proposal.lst_start_end_time.strftime("%H:%M:%S")} {proposal.night_obs} {proposal.avoid_sunrise_sunset}'
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
            ax.set_title(f'Weekly Timetable: {scheduled_proposals} of {total_scheduled_proposals} over {total_proposals} Proposals (Week {week_num + 1})', fontsize=16)

            # Add gridlines for better readability
            ax.yaxis.grid(True)

            # Create a legend outside the plot
            handles = [plt.Rectangle((0, 0), 1, 1, color=color) for color in legend_dict.values()]
            ax.legend(handles, legend_dict.keys(), title="Proposals", loc='upper left', bbox_to_anchor=(1, 1))

            # Save the plot to a file
            filename =  f"outputs/week_{week_start_date.strftime('%Y-%m-%d')}-{week_end_date.strftime('%Y-%m-%d')}.png"
            plt.tight_layout()
            plt.savefig(filename, dpi=200)  # Save the figure as a PNG file
            plt.close(fig)  # Close the figure to free up memory


