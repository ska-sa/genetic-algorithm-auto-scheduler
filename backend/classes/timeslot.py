from datetime import datetime


class Timeslot():
    def __init__(self, id: int, start_datetime: datetime, end_datetime: datetime) -> None:
        self.id: int = id
        self.start_time: datetime = start_datetime
        self.end_time: datetime = end_datetime

    def get_duration(self) -> int:
        """
        Returns the duration of the timeslot in seconds.
        """
        return int((self.end_time - self.start_time).total_seconds())

