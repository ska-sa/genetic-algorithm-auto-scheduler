from .timeslot import Timeslot
from .proposal import Proposal

class Utils():
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_timeslot_by_id(self, timeslot_id: int) -> Timeslot:
        return next((t for t in TIMESLOTS if t.id == timeslot_id), None)

    @staticmethod
    def get_proposal_by_id(self, proposal_id: int) -> Proposal:
        return next((p for p in PROPOSALS if p.id == proposal_id), None)