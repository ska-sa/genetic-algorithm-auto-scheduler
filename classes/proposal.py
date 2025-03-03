from datetime import date, time

class Proposal():
    def __init__(self, id: int, owner_email: str, build_time: int, prefered_dates_start: list[date], prefered_dates_end: list[date], avoid_dates_start: list[date], avoid_dates_end: list[date], night_obs: bool, avoid_sunrise_sunset: bool, minimum_antennas: int, lst_start_time: time, lst_start_end_time: time, simulated_duration: int, score: float) -> None:
        self.id: int = id
        self.owner_email: str = owner_email
        self.build_time: int = build_time
        self.prefered_dates_start: list[date] = prefered_dates_start
        self.prefered_dates_end: list[date] = prefered_dates_end
        self.avoid_dates_start: list[date] = avoid_dates_start
        self.avoid_dates_end: list[date] = avoid_dates_end
        self.night_obs: bool = night_obs
        self.avoid_sunrise_sunset: bool = avoid_sunrise_sunset
        self.minimum_antennas: int = minimum_antennas
        self.lst_start_time: time = lst_start_time
        self.lst_start_end_time: time = lst_start_end_time
        self.simulated_duration: int = simulated_duration
        self.score: int = score

    @staticmethod
    def parse_time(time_str: str) -> time:
        """
        Parse a time string in the format "HH:MM" and return a datetime.time object.
        """
        hour, minute = map(int, time_str.split(":"))
        return time(hour, minute)
    
    def get_score(self):
        return 1