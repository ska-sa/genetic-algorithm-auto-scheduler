import random
from datetime import datetime, timedelta, date, time
from ga.proposal import Proposal
from .utils import get_night_window, get_sunrise_sunset, get_proposal_by_id, all_constraints_met
from matplotlib import pyplot as plt
import copy

class Timetable(Individual):
    def __init__(self, start_date: date, end_date: date, proposals: Proposal, schedules: list[list[int]] = []):
        super.__init__(start_date, end_date, proposals, schedules)
        self.proposals: Proposal = proposals
        self.start_date: date = start_date
        self.end_date: date = end_date
        if schedules == []:
            self.schedules = list()
            self.generate()
        else:
            self.schedules = schedules
    
    def remove_clashing_proposals(self) -> None:
        return
    

    def plot(self):
        # Define days of the week and colors
        days_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        colors = ['gray', 'yellow', 'blue', 'red', 'green', 'brown', 'pink', 
                'lightgreen', 'lightblue', 'wheat', 'salmon', 'lightcoral', 'lightyellow']

        # Calculate the start and end dates of the timetable
        start_date = min(schedule[1] for schedule in self.schedules if schedule[1] is not None).date()
        end_date = max(schedule[1] + timedelta(seconds=get_proposal_by_id(self.proposals, schedule[0]).simulated_duration)
                    for schedule in self.schedules if schedule[1] is not None).date()

        # Calculate the number of weeks between the start and end dates
        num_weeks = (end_date - start_date).days // 7 + 1

        # Get total number of schduled proposals
        total_scheduled_proposals = sum(1 for schedule in self.schedules if schedule[1] is not None)

        for week_num in range(num_weeks):
            # Calculate the start and end dates of the current week
            week_start_date = start_date + timedelta(days=week_num * 7)
            week_end_date = week_start_date + timedelta(days=6)

            # Create a figure for plotting
            fig, ax = plt.subplots(figsize=(12, 8))

            # Dictionary to hold color legend
            legend_dict = {}

            # Total number of proposals
            total_proposals = len(self.schedules)
            scheduled_proposals = 0

            # Iterate through schedules to plot each proposal
            for idx, (proposal_id, start_datetime) in enumerate(self.schedules):
                if start_datetime is not None and week_start_date <= start_datetime.date() <= week_end_date:
                    scheduled_proposals += 1  # Count scheduled proposals
                    proposal: Proposal = get_proposal_by_id(self.proposals, proposal_id)
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


