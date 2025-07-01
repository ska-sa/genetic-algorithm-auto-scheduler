from dataclasses import dataclass
from datetime import datetime

@dataclass
class Schedule:
    proposal_id: int
    start_datetime: datetime
