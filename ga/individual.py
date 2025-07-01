from datetime import date
from .proposal import Proposal
from .schedule import Schedule
from .utils import *
from dataclasses import astuple

class Individual:
    """
    An Individual represents a candidate solution in an optimization problem, typically in the context of evolutionary algorithms.
    """
    def __init__(self, start_date: date, end_date: date, proposals: list[Proposal], schedules: list[Schedule] = []):
        """
        Initialize an Individual object.

        Args:
            start_date (date): The start date of the Individual's planning horizon.
            end_date (date): The end date of the Individual's planning horizon.
            proposals (list[Proposal]): A list of Proposal objects associated with the Individual.
            schedules (list[Schedule], optional): A list of Schedule objects associated with the Individual. If not provided, the `generate()` method will be called to generate the schedules.

        Returns:
            None
        """
        self.proposals: list[Proposal] = proposals
        self.start_date: date = start_date
        self.end_date: date = end_date
        if schedules == []:
            self.schedules = list()
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
        for proposal in self.proposals:
            start_datetime = generate_datetime(proposal, self.start_date, self.end_date) if random.random() > 0.75 else None
            self.schedules.append(Schedule(proposal.id, start_datetime))
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

        for schedule in self.schedules:
            proposal_id: int
            start_datetime: datetime
            proposal_id, start_datetime = astuple(schedule)  # unpack Schedule's attr
            proposal: Proposal = get_proposal_by_id(self.proposals, proposal_id)
            total_proposal_duration += proposal.simulated_duration
            if start_datetime is not None:
                num_scheduled_proposals += 1
                for another_schedule in self.schedules:
                    another_proposal_id, another_proposal_start_datetime = astuple(another_schedule)
                    another_proposal: Proposal = get_proposal_by_id(self.proposals, another_proposal_id)
                    if (proposal_id != another_proposal_id):
                        if another_proposal_start_datetime is not None:
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
                        else:
                            total_unscheduled_time += proposal.simulated_duration
            else:
                total_unscheduled_time += proposal.simulated_duration

        # If no proposals are scheduled, return a score of 0
        if num_scheduled_proposals == 0:
            return 0.0 
        # Return the score as a fraction of non-clash time to total time
        return ((total_proposal_duration - total_clash_time) / (total_proposal_duration)) * (0.95 ** (len(self.schedules) - num_scheduled_proposals))
 
    def crossover(self, schedules: list[Schedule]) -> list[Schedule]:
        """
        Perform crossover between the schedules of the current Individual and the provided schedules.

        Args:
            schedules (list[Schedule]): The schedules of another Individual to be used in the crossover operation.

        Returns:
            list[Schedule]: The offspring's schedules resulting from the crossover operation.
        """
        offspring_schedules: list[Schedule] = list()
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
                proposal_id = original_schedules[mutation_index].proposal_id  # Get proposal_id
                proposal: Proposal = get_proposal_by_id(self.proposals, proposal_id)
                start_datetime = generate_datetime(proposal, self.start_date, self.end_date) if random.random() > 0.75 else None  # Compute new start_datetime
                
                # Mutate the copied schedule
                original_schedules[mutation_index].start_datetime = start_datetime  # Mutate the start_datetime at this mutation index
                mutation_indexes.append(mutation_index)

        # Update self.schedules with the mutated schedules
        self.schedules = original_schedules