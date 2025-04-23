# Genetic Algorithim Auto Scheduler

## Description

The current manual method of scheduling radio astronomy observations at South African Radio Astronomy Observatory (SARAO) is erroneous, time-consuming, and labor-intensive. This has resulted in the underutilization of their telescopes, hence negatively impacting revenue. The goal of this project is to maximize the utilization of the SARAO telescopes by proposing an Auto Scheduler that uses a Genetic Algorithm to schedule radio astronmoy observations for the user defined start and end date of the week without compromising any contraints.

## What is Genetic Algorithm

Genetic Algorithm is a computer science technique that uses natural selection and genetic operations to find the best solution to a problem.

## Genetic Operations

- Encoding of a solution as an Individual.
- Generating a list of individuals to form a Population.
- Computing an Individual's fitness in terms of the contraints.
- Evolution of Individuals in a Population over N generations.
    - Selection of the fittest Individuals as Parents.
    - Crossover or Mating, which copies genetic material from Parents to Offsprings.
    - Mutation, which modifies the genetic material of the generated Offsprings.
- Decoding the fittest individuals after N generation, yielding to be best solution.

## Advanatges of GA

- Global optimization: as it explore the entire solution space, hence avoiding local optima.
- Adaptability and versatility: as it can be adapted to various optimization problems, including those with continuous, discrete, and multi-objective constraints.
- Parallelism: the population of solutions, allows for easy parallel processing.

## Disadvantages of GA

- Computational Cost: as it can be computationally intensive, especially for large-scale problems.
- Parameter Tuning: finding the optimal settings for parameters like population size, mutation rate, and crossover probabilities.
- Lack of Guarantee: as there's no guarantee that a genetic algorithm will converge to a global optimum.

## Contraints

- Proposal's priority or score.
- Proposal's lst start, and lst start end.
- Proposal's night observation.
- Proposal's avoid sunrise and sunset.
- Plane arrival and depart timeslots*.
- Proposal's build time*.
- Proposal's required number of antennas*.

## Objectives

- Implement a script that take predefined start and end date of the week, then read a CSV file of proposals then generate a timetable of those proposals of that week and output the generated timetable as a PNG image.  

## UML CLass Diagrams

## Implementation

- We encode a timetable as a list of list of two integers timeslot id, and proposal id, in this formart.
- timetable = [[timeslot_0_id, propsal_0_id], ..., [timeslot_n_id, proposal_n_id]]
- These id's are used to access the the acttual timeslot and proposal from TIMESLOT, and PROPOSALS which containts timeslots and proposals that has the following data fields. 
- timeslot:
-   - id: int
-   - start_dateime: datetime
-   - end_datetime: datetime

- proposal:
-   - id: int
-   - owner_email: str
-   - build_time: int
-   - prefered_dates_start: list[date]
-   - prefered_dates_end: list[date]
-   - avoid_dates_start: list[date]
-   - avoid_dates_end: list[date]
-   - night_obs: bool
-   - avoid_sunrise_sunset: bool
-   - minimum_antennas: int
-   - lst_start_time: time
-   - lst_start_end_time: time
-   - simulated_duration: int
-   - score: int

- We then utilize genetic algorithms processe like:
-   - timetables generation
-   - timetable rating, and selection
-   - timetable cross over
-   - timetable mutation

- It worth noting that the following constraints were considered when calculating the score/fitness of each timtable:
-   - Proposal's score/priority
-   - Proposal's LST start and start end time
-   - Proposal's timeslot gaps
-   - Proposal's number of allocated timeslots compared with its duration
-   - Proposal's night observations condition
-   - Proposal's avoid sunsrise/sunset condition
-   - Proposal's minimum number of antennas compared with available antenna (future work)

- Over a predefined number of generations we get the best fit timetable.

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