import random
import copy
from datetime import date, datetime, timedelta
from .proposal import Proposal
from .utils import get_global_vars

START_DATE: date = date.today()
END_DATE: date = date.today()
PROPOSALS: list[Proposal] = []

def generate_random_date() -> date:
    """
    Randomly generates a date between START_DATE and END_DATE.

    Args:
        None

    Returns:
        date: A randomly generated date between START_DATE and END_DATE.
    """
    delta_days: int = (END_DATE - START_DATE).days
    days: int = random.randint(0, delta_days)
    return START_DATE + timedelta(days=days)

def generate_random_start_datetime(proposal: Proposal) -> datetime|None:
    """
    Generates a random start datetime for a proposal, ensuring that all constraints are met.

    Args:
        proposal (Proposal): The proposal object for which to generate a random start datetime.

    Returns:
        datetime|None: A randomly generated start datetime that meets all constraints, or None if no valid datetime could be found.
    """
    for _ in range(5):
        if random.random() > 0.75:
            break
        start_date = generate_random_date()
        earliest_datetime = datetime.combine(date=start_date, time=proposal.lst_start_time)
        latest_datetime = datetime.combine(date=start_date, time=proposal.lst_start_end_time)
        delta_seconds = (latest_datetime - earliest_datetime).seconds
        seconds = random.randint(0, delta_seconds)
        proposed_start_datetime:datetime = earliest_datetime + timedelta(seconds=seconds)
        if proposal.all_constraints_met(proposed_start_datetime):
            return proposed_start_datetime
    return None

class Individual:
    """
    An Individual represents a candidate solution in an optimization problem, typically in the context of evolutionary algorithms.
    """
    def __init__(self, schedules: list[Proposal] = []):
        """
        Initialize an Individual object.

        Args:
            schedules (list[Schedule], optional): A list of Schedule objects associated with the Individual. If not provided, the `generate()` method will be called to generate the schedules.

        Returns:
            None
        """
        global START_DATE, END_DATE, PROPOSALS
        START_DATE, END_DATE, proposals_dict = get_global_vars()
        PROPOSALS = [Proposal.from_dict(p) for p in proposals_dict]
        self.schedules: list[Proposal] = []
        if schedules == []:
            self.generate()
        else:
            self.schedules = schedules

    def generate(self) -> None:
        """
        Generate schedules from proposals for an Individual.

        Args:
            None

        Returns:
            None
        """
        global PROPOSALS
        for proposal in PROPOSALS:
            start_datetime = generate_random_start_datetime(proposal) if random.random() > 0.75 else None
            schedule_proposal: Proposal = proposal
            schedule_proposal.scheduled_start_datetime = start_datetime
            self.schedules.append(schedule_proposal)
        return
        
    def compute_fitness(self) -> float:
        """
        Compute the fitness of the Individual based on the scheduled proposals and potential clashes.

        Args:
            None

        Returns:
            float: The fitness score of the Individual, ranging from 0.0 (worst) to 1.0 (best).
        """
        total_proposal_duration: int = 0
        total_clash_time: float = 0
        total_unscheduled_time: int = 0
        num_scheduled_proposals: int = 0

        for proposal in self.schedules:
            total_proposal_duration += proposal.simulated_duration
            if proposal.scheduled_start_datetime is not None:
                num_scheduled_proposals += 1
                for another_proposal in self.schedules:
                    if (proposal.id != another_proposal.id):
                        if another_proposal.scheduled_start_datetime is not None:
                            # Calculate end times for both proposals
                            proposal_end_datetime = proposal.scheduled_start_datetime + timedelta(seconds=proposal.simulated_duration)
                            another_proposal_end_datetime = another_proposal.scheduled_start_datetime + timedelta(seconds=another_proposal.simulated_duration)

                            # Check for clash
                            # Calculate clash time
                            max_start = max(proposal.scheduled_start_datetime, another_proposal.scheduled_start_datetime)
                            min_end = min(proposal_end_datetime, another_proposal_end_datetime)
                            
                            # Calculate clash time in seconds
                            clash_time = max(0, (min_end - max_start).total_seconds())
                            total_clash_time += clash_time
                        else:
                            total_unscheduled_time += proposal.simulated_duration
            else:
                total_unscheduled_time += proposal.simulated_duration

        # If no proposals are scheduled, return a score of 0
        if num_scheduled_proposals == 0:
            return 0.0 
        # Return the score as a fraction of non-clash time to total time
        return ((total_proposal_duration - total_clash_time) / (total_proposal_duration)) * (0.95 ** (len(self.schedules) - num_scheduled_proposals))
 
    def crossover(self, schedules: list[Proposal]) -> list[Proposal]:
        """
        Perform crossover between the schedules of the current Individual and the provided schedules.

        Args:
            schedules (list[Proposa]): The schedules of another Individual to be used in the crossover operation.

        Returns:
            list[Proposal]: The offspring's schedules resulting from the crossover operation.
        """
        offspring_schedules: list[Proposal] = list()
        for schedule_1, schedule_2 in zip(self.schedules, schedules):
            offspring_schedules.append(schedule_1 if random.random() > 0.5 else schedule_2)
        return offspring_schedules
    
    def mutation(self, mutation_rate: float = 0.3) -> None:
        """
        Perform mutation on the schedules of the Individual.

        Args:
            mutation_rate (float, optional): The rate of mutation, ranging from 0.0 to 1.0. Defaults to 0.3.

        Returns:
            None
        """
        num_of_mutable_schedules: int = int(len(self.schedules) * mutation_rate)
        mutation_indexes: list[int] = list()  # Use a set for unique mutation indexes

        # Create a deep copy of the schedules to avoid modifying the original
        original_schedules = copy.deepcopy(self.schedules)

        while len(mutation_indexes) < num_of_mutable_schedules:
            mutation_index = random.randint(0, len(original_schedules) - 1)
            
            if mutation_index not in mutation_indexes:
                proposal: Proposal = original_schedules[mutation_index]
                start_datetime = generate_random_start_datetime(proposal) if random.random() > 0.75 else None  # Compute new start_datetime
                
                # Mutate the copied schedule
                original_schedules[mutation_index].scheduled_start_datetime = start_datetime  # Mutate the start_datetime at this mutation index
                mutation_indexes.append(mutation_index)

        # Update self.schedules with the mutated schedules
        self.schedules = original_schedules