# Auto-Scheduler

## Description

The current manual method of scheduling radio astronomy observations at SARAO is error-prone, time-consuming, and labor-intensive. This has resulted in the underutilization of the telescopes, negatively impacting revenue. The goal of this project is to maximize the utilization of the SARAO telescopes by proposing an auto-scheduler that uses a Genetic Algorithm to schedule observations for the upcoming week without conflicts.

## Working principle
We encode a timetable as a list of list of two integers timeslot id, and proposal id, in this formart.
timetable = [
    [timeslot_0_id, propsal_0_id],
    .
    .
    .
    [timeslot_n_id, proposal_n_id]
]
These id's are used to access the the acttual timeslot and proposal from TIMESLOT, and PROPOSALS which containts timeslots and proposals that has the following data fields. 
timeslot:
    - id: int
    - start_dateime: datetime
    - end_datetime: datetime

proposal:
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
    lst_start_time: time
    lst_start_end_time: time
    simulated_duration: int
    score: int

We then utilize genetic algorithms processe like:
    timetables generation
    timetable rating, and selection
    timetable cross over
    timetable mutation

Over a predefined number of generations we get the best fit timetable.

## File Structure

- **classes/**: Contains the class definitions used in the project.
- **outputs/**: Contains the .PNG output images of the generated weakly timetable.
- **proposals/csv**: Contains the excel spreadsheet of proposals (excluded from git).
- **tests/**: Contains the pytest unit tests for this project.
- **venv/**: Virtual environment for Python dependencies (excluded from git).
- **.dockerignore**: Specifies files to ignore when building Docker images.
- **.gitignore**: Specifies files to ignore in version control.
- **Dockerfile**: Contains the instructions to build the Docker image for the project.
- **main.py**: The main entry point for the application.
- **Makefile**: Defines the custom cli cmd for automate admin task of the project.
- **README.md**: This project description file.
- **requirements.txt**: Lists the dependencies required for the project.

## Cloning the Project

To clone the project, run the following command in your terminal:

```git clone https://github.com/shlabisa/auto-scheduler.git```

Make sure you are within the project folder, if not. Then use:

```cd Auto-Sheduler```

### Installing the Dependencies

To install the dependecies:

```virtualenv venv```

```. venv/bin/activate```

```venv/bin/python -m pip install -r requirements.txt```

### Running the Code

To run the project:

```venv/bin/python main.py```

To build a docker image:

```docker build -t auto-schedular .```

To run the docker image:

```docker run auto-schedular```

### Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

### License

- You can use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.
- Attribution is required when using or distributing the code.
- This software is provided 'as is', without any express or implied warranty. Use at your own risk.