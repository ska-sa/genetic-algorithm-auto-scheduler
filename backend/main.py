import uvicorn
from datetime import date, datetime
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ga import Proposal, Individual, Genetic_Algorithm, Timetable, update_global_vars, parse_time

class ProposalModel(BaseModel):
    """Model representing a proposal."""
    id: str
    description: str
    proposal_id: str
    owner_email: str
    instrument_product: str
    instrument_integration_time: str
    instrument_band: str
    instrument_pool_resources: str
    lst_start: str
    lst_start_end: str
    simulated_duration: str
    night_obs: str
    avoid_sunrise_sunset: str
    minimum_antennas: str
    general_comments: str
    scheduled_start_datetime: str
    

class CreateTimetableRequestModel(BaseModel):
    """Request model for creating a timetable."""
    start_date: str
    end_date: str
    proposals: list[ProposalModel]


class TimetableModel(CreateTimetableRequestModel):
    """Model representing a timetable."""
    id: int
    name: str
    class Config:
        from_attributes = True


app = FastAPI()
router_url_prefix = "/api/v1/timetables/"

timetables: list[TimetableModel] = []

origins = [
    "http://localhost:4200",  # Angular app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    """
    Root endpoint to check if the API is running.

    Returns:
        JSON message indicating the API is running.
    """
    return {"message": "Welcome to the Genetic Algorithim based Auto Scheduler API"}

@app.get(router_url_prefix, response_model=list[TimetableModel])
def get_timetables():
    """
    Gets a list of all timetables.

    Args:
        None
    
    Returns:
        JSON list of all timetables.
        If no timetables exist, returns an empty list.
    """
    global timetables
    return timetables

@app.get(router_url_prefix+"{timetable_id}", response_model=TimetableModel)
def get_timetable(timetable_id: int):
    """
    Gets a timetable of a specific id.

    Args:
        proposal_id (int): ID of the timetable to be retrieved.

    Returns:
        JSON object of the timetable with the specified ID.
        If not found, returns an empty JSON object.
    """
    global timetables
    return next((t for t in timetables if t.id == timetable_id), {})

@app.post(router_url_prefix, response_model=TimetableModel)
def create_timetable(create_timetable_request: CreateTimetableRequestModel):
    """
    Generates a new timetable based on the provided proposals using Genetic Algorithm .

    Args:
        create_timetable_request (CreateTimetableRequestModel): Request model containing start date, end date, and proposals.

    Returns:
        JSON object of the newly generated timetable.
    """
    global timetables
    timetable_id = len(timetables) + 1
    start_date: date = datetime.strptime(create_timetable_request.start_date, "%Y-%m-%d").date()
    end_date: date = datetime.strptime(create_timetable_request.end_date, "%Y-%m-%d").date()
    proposals: list[Proposal] = []
    for p in create_timetable_request.proposals:
        proposal: Proposal = Proposal(
            id=int(p.id),
            description=p.description,
            proposal_id=p.proposal_id,
            owner_email=p.owner_email,
            instrument_product=p.instrument_product,
            instrument_integration_time=float(p.instrument_integration_time),
            instrument_band=p.instrument_band,
            instrument_pool_resources=p.instrument_pool_resources,
            lst_start_time=parse_time(p.lst_start),
            lst_start_end_time=parse_time(p.lst_start_end),
            simulated_duration=int(p.simulated_duration),
            night_obs=p.night_obs.lower() == "yes",
            avoid_sunrise_sunset=p.avoid_sunrise_sunset.lower() == "yes",
            minimum_antennas=int(p.minimum_antennas),
            general_comments=p.general_comments,
            scheduled_start_datetime=None,
        )
        proposals.append(proposal)


    update_global_vars(start_date=start_date, end_date=end_date, proposals=[p.to_dict() for p in proposals])

    # Generate the individuals using the genetic algorithm
    genetic_algorithm: Genetic_Algorithm = Genetic_Algorithm(num_of_individuals=10, num_of_generations=50)
    
    # Get the best individual from the genetic algorithm
    scheduled_proposals: list[Proposal] = genetic_algorithm.get_best_fit_individual().schedules
    
    # Visualize the best timetable
    best_timetable: Timetable = Timetable(schedules=scheduled_proposals)
    best_timetable.plot() # Plot raw timetable after genetic algorithm
    best_timetable.remove_clashes()
    best_timetable.plot(filename_suffix="_clash_free")# Plot the timetable after removing clashes

    scheduled_proposals_models: list[ProposalModel] = []
    for s in best_timetable.schedules:
        scheduled_proposals_models.append(ProposalModel(
            id=str(s.id),
            description=s.description,
            proposal_id=s.proposal_id,
            owner_email=s.owner_email,
            instrument_product=s.instrument_product,
            instrument_integration_time=str(s.instrument_integration_time),
            instrument_band=s.instrument_band,
            instrument_pool_resources=s.instrument_pool_resources,
            lst_start=s.lst_start_time.strftime("%H:%M"),
            lst_start_end=s.lst_start_end_time.strftime("%H:%M"),
            simulated_duration=str(s.simulated_duration),
            night_obs="yes" if s.night_obs else "no",
            avoid_sunrise_sunset="yes" if s.avoid_sunrise_sunset else "no",
            minimum_antennas=str(s.minimum_antennas),
            general_comments=s.general_comments,
            scheduled_start_datetime=s.scheduled_start_datetime.strftime("%Y-%m-%d %H:%M:%S") if s.scheduled_start_datetime else ""
            )
        )
    import random
    names = [
        "Alpha", "Bravo", "Charlie", "Delta", "Echo", 
        "Foxtrot", "Golf", "Hotel", "India", "Juliett",
        "Kilo", "Lima", "Mike", "Hopewell", "Oscar",
        "Papa", "Quebec", "Romeo", "Sierra", "Tango",
        "Ester", "Quad", "Jovian", "Lilly", "Agile"
    ]
    name = random.choice(names)
    timetable = TimetableModel(id=timetable_id, name=name, start_date=create_timetable_request.start_date, end_date=create_timetable_request.end_date, proposals=scheduled_proposals_models)
    timetables.append(timetable)
    return timetable

@app.put(router_url_prefix+"{timetable_id}", response_model=TimetableModel)
def update_timetable(timetable_id: int, timetable: TimetableModel):
    """
    Updates an existing timetable by passing it back to the genetic algorithm.

    Args:
        timetable_id (int): ID of the timetable to be updated.
        timetable (Timetable): Updated timetable data.

    Returns:
        JSON object of the updated timetable.
        If not found, returns an empty JSON object.
    """
    global timetables
    for t in timetables:
        if t.id == timetable_id:
            t.proposals = timetable.proposals
            start_date: date = datetime.strptime(t.start_date, "%Y-%m-%d").date()
            end_date: date = datetime.strptime(t.end_date, "%Y-%m-%d").date()
            print
            proposals: list[Proposal] = list()
            for p in t.proposals:
                proposal: Proposal = Proposal(
                    id=int(p.id),
                    description=p.description,
                    proposal_id=p.proposal_id,
                    owner_email=p.owner_email,
                    instrument_product=p.instrument_product,
                    instrument_integration_time=float(p.instrument_integration_time),
                    instrument_band=p.instrument_band,
                    instrument_pool_resources=p.instrument_pool_resources,
                    lst_start_time=parse_time(p.lst_start),
                    lst_start_end_time=parse_time(p.lst_start_end),
                    simulated_duration=int(p.simulated_duration),
                    night_obs=p.night_obs.lower() == "yes",
                    avoid_sunrise_sunset=p.avoid_sunrise_sunset.lower() == "yes",
                    minimum_antennas=int(p.minimum_antennas),
                    general_comments=p.general_comments,
                    scheduled_start_datetime=datetime.strptime(p.scheduled_start_datetime, "%Y-%m-%d %H:%M:%S") if p.scheduled_start_datetime else None,
                )
                proposals.append(proposal)
            
            update_global_vars(start_date=start_date, end_date=end_date, proposals=[p.to_dict() for p in proposals])

            initial_individuals: list[Individual] = [
                Individual(schedules=proposals)
            ]

            ga: Genetic_Algorithm = Genetic_Algorithm(initial_individuals=initial_individuals, num_of_individuals=10, num_of_generations=50)
            scheduled_proposals: list[Proposal] = ga.get_best_fit_individual().schedules

            timetable = TimetableModel(
                id=t.id,
                name=t.name,
                start_date=t.start_date,
                end_date=t.end_date,
                proposals=[
                    ProposalModel(
                        id=str(s.id),
                        description=s.description,
                        proposal_id=s.proposal_id,
                        owner_email=s.owner_email,
                        instrument_product=s.instrument_product,
                        instrument_integration_time=str(s.instrument_integration_time),
                        instrument_band=s.instrument_band,
                        instrument_pool_resources=s.instrument_pool_resources,
                        lst_start=s.lst_start_time.strftime("%H:%M"),
                        lst_start_end=s.lst_start_end_time.strftime("%H:%M"),
                        simulated_duration=str(s.simulated_duration),
                        night_obs="yes" if s.night_obs else "no",
                        avoid_sunrise_sunset="yes" if s.avoid_sunrise_sunset else "no",
                        minimum_antennas=str(s.minimum_antennas),
                        general_comments=s.general_comments,
                        scheduled_start_datetime=s.scheduled_start_datetime.strftime("%Y-%m-%d %H:%M:%S") if s.scheduled_start_datetime else ""
                    ) for s in scheduled_proposals
                ]
            )

            best_timetable: Timetable = Timetable(schedules=scheduled_proposals)
            best_timetable.plot("_updated") # Plot raw updated timetable after genetic algorithm
            best_timetable.remove_clashes()
            best_timetable.plot(filename_suffix="_clash_free_updated")# Plot the updated timetable after removing clashes

            timetables = [t if t.id != timetable_id else timetable for t in timetables]

            return t
    return {}

@app.delete(router_url_prefix+"{timetable_id}", response_model=TimetableModel)
def delete_timetable(timetable_id: int):
    """
    Deletes a timetable by its ID.

    Args:
        timetable_id (int): ID of the timetable to be deleted.

    Returns:
        JSON object of deleted timetable.
        If not found, returns an empty JSON object.
    """
    global timetables
    timetable: TimetableModel = get_timetable(timetable_id)
    timetables = [t for t in timetables if t.id != timetable_id]
    return timetable

def main():
    uvicorn.run(app=app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()