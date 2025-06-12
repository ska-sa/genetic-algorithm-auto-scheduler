from fastapi import FastAPI, Body
from datetime import date
from pydantic import BaseModel
from ga import Proposal, Timetable, Genetic_Algorithm, get_proposal_by_id
import os
import random

BASE_URL = "/api/v1"
app = FastAPI()

class ProposalModel(BaseModel):
    id: int
    owner_email: str
    build_time: int
    prefered_dates_start: list[date]
    prefered_dates_end: list[date]
    avoid_dates_start: list[date]
    avoid_dates_end: list[date]
    night_obs: bool
    avoid_sunrise_sunset: bool
    minimum_antennas: int
    lst_start_time: str
    lst_start_end_time: str
    simulated_duration: int
    score: float

class ProposalInput(BaseModel):
    start_date: date
    end_date: date
    proposals: list[ProposalModel]

@app.post(f"{BASE_URL}/timetables")
def generate_timetable(proposal_input: ProposalInput):
    # Generate the timetable using the genetic algorithm
    proposals: list[Proposal] = list()
    for proposal in proposal_input.proposals:
        proposals.append(Proposal(
            id=proposal.id,
            owner_email=proposal.owner_email,
            build_time=proposal.build_time,
            prefered_dates_start=proposal.prefered_dates_start,
            prefered_dates_end=proposal.prefered_dates_end,
            avoid_dates_start=proposal.avoid_dates_start,
            avoid_dates_end=proposal.avoid_dates_end,
            night_obs=proposal.night_obs,
            avoid_sunrise_sunset=proposal.avoid_sunrise_sunset,
            minimum_antennas=proposal.minimum_antennas,
            lst_start_time=Proposal.parse_time(proposal.lst_start_time),
            lst_start_end_time=Proposal.parse_time(proposal.lst_start_end_time),
            simulated_duration=proposal.simulated_duration,
            score=proposal.score
        ))
    random.shuffle(proposals)  # Shuffle proposals for randomness
    genetic_algorithm: Genetic_Algorithm = Genetic_Algorithm(
        start_date=proposal_input.start_date,
        end_date=proposal_input.end_date,
        proposals=proposals,
        num_of_timetables=10,
        num_of_generations=100
    )
    # Get the best timetable from the genetic algorithm
    best_timetable: Timetable = genetic_algorithm.get_best_fit_timetable()

    proposal_schedules = [{"proposal": get_proposal_by_id(proposals, proposal_id).__dict__, "start_datetime": start_datetime_str} for proposal_id, start_datetime_str in best_timetable.schedules]
    
    # Convert the best timetable to a dictionary
    timetable_dict = {
        "start_date": best_timetable.start_date.isoformat(),
        "end_date": best_timetable.end_date.isoformat(),
        "schedules": proposal_schedules
    }

    return timetable_dict


"""
# Test curl command:
curl -X POST "http://localhost:8000/api/v1/timetables" \
    -H "Content-Type: application/json" \
    -d '{
        "start_date": "2024-01-01", "end_date": "2024-01-22", 
        "proposals": [
            {
                "id": 20241221141256,
                "owner_email": "mar.arabsalmani@gmail.com",
                "build_time": 1800,
                "prefered_dates_start": [],
                "prefered_dates_end": [],
                "avoid_dates_start": [],
                "avoid_dates_end": [],
                "night_obs": false,
                "avoid_sunrise_sunset": false,
                "minimum_antennas": 58,
                "lst_start_time": "06:00:00",
                "lst_start_end_time": "11:30:00",
                "simulated_duration": 18407,
                "score": 1
            },
            {
                "id": 20241208155301,
                "owner_email": "mancerapavel@gmail.com",
                "build_time": 1800,
                "prefered_dates_start": [],
                "prefered_dates_end": [],
                "avoid_dates_start": [],
                "avoid_dates_end": [],
                "night_obs": false,
                "avoid_sunrise_sunset": false,
                "minimum_antennas": 58,
                "lst_start_time": "06:00:00",
                "lst_start_end_time": "07:25:00",
                "simulated_duration": 18124,
                "score": 3
            }
        ]
    }
    '
# Response:
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-22",
  "schedules": [
    {
      "proposal": {
        "id": 20241221141256,
        "owner_email": "mar.arabsalmani@gmail.com",
        "build_time": 1800,
        "prefered_dates_start": [],
        "prefered_dates_end": [],
        "avoid_dates_start": [],
        "avoid_dates_end": [],
        "night_obs": false,
        "avoid_sunrise_sunset": false,
        "minimum_antennas": 58,
        "lst_start_time": "06:00:00",
        "lst_start_end_time": "11:30:00",
        "simulated_duration": 18407,
        "score": 1.0
      },
      "start_datetime": "2024-01-11T07:16:00"
    },
    {
      "proposal": {
        "id": 20241208155301,
        "owner_email": "mancerapavel@gmail.com",
        "build_time": 1800,
        "prefered_dates_start": [],
        "prefered_dates_end": [],
        "avoid_dates_start": [],
        "avoid_dates_end": [],
        "night_obs": false,
        "avoid_sunrise_sunset": false,
        "minimum_antennas": 58,
        "lst_start_time": "06:00:00",
        "lst_start_end_time": "07:25:00",
        "simulated_duration": 18124,
        "score": 3.0
      },
      "start_datetime": "2024-01-12T06:47:10"
    }
  ]
}
"""

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()