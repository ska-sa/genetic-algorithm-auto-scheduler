# Genetic Algorithm Auto Scheduler

## Description

- The current manual method of scheduling radio astronomy observations at the South African Radio Astronomy Observatory (SARAO) is erroneous, time-consuming, and labor-intensive. 

- This has resulted in the underutilization of their telescopes, hence negatively impacting revenue. 

- The goal of this project is to maximize the utilization of the SARAO telescopes by proposing an Auto Scheduler that uses Genetic Algorithm (GA) to schedule radio astronomy observations for the user-defined start and end dates of the timetable without compromising any constraints.

## Getting Started

### Cloning the Repository

- `git clone https://github.com/ska-sa/genetic-algorithm-auto-scheduler`

### Running thr Backend:

- Open new terminal, and `cd backend`.

- Create Virtual Environment `virtualenv venv`.

- Activate Virtual Environment `. venv/bin/activate`.

- Please download the sensitive CSV file from [Proposals CSV File](https://drive.google.com/file/d/1uKx0ocyvraKuRoVFqLJ_8v3jRMwQrhCL/view).

- Move the downloaded CSV file into the `proposals/csv/`.

- Rename the file to `ObsList.csv`.

- Install dependecies `pip install -r requirements.txt`.

- Run backend script `python main.py`, this should generate timetable images into `outputs/`.

### Running entire Application with Docker Compose

- Open new terminal.

- Build and start app containers `docker-compose up --build`.

### File Structure

- **backend/**: For the backend files including the GA module.

- **fake/**: For Fake KATStore and ObsData API (Todo).

- **res**: Contains images used in the README.md.

- **.gitignore**: Specifies files to ignore in version control.

- **docker-compose.yaml**: Defines Docker container configuration.

- **README.md**: This project description file.

## What is Genetic Algorithm?

- Genetic Algorithm is a computer science technique that uses natural selection and genetic operations to find the best solution to a problem.

## Genetic Operations

- Encoding of a solution as an Individual.

- Generating a list of individuals to form a Population.

- Computing an Individual's fitness in terms of the constraints.

- Evolution of Individuals in a Population over N Generations.

- Selection of the fittest Individuals as Parents.

- Crossover or Mating, which copies genetic material from Parents to Offspring.

- Mutation, which modifies the genetic material of the generated Offspring.

- Decoding the fittest individuals after N Generations, yielding the best solution.

## Advantages of GA

- Global optimization: As it explores the entire solution space, hence avoiding local optima.

- Adaptability and versatility: It can be adapted to various optimization problems, including those with continuous, discrete, and multi-objective constraints.

- Parallelism: The population of solutions allows for easy parallel processing.

## Disadvantages of GA

- Computational Cost: It can be computationally intensive, especially for large-scale problems.

- Parameter Tuning: Finding the optimal settings for parameters like population size, mutation rate, and crossover probabilities.

- Lack of Guarantee: There's no guarantee that a genetic algorithm will converge to a global optimum.

## Constraints

- Proposal's priority or score.

- Proposal's lst start, and lst start end.

- Proposal's night observation.

- Proposal's avoid sunrise and sunset.

- Plane arrival and departure timeslots*.

- Proposal's build time*.

- Proposal's required number of antennas*.

## Objectives

- The goal of this project is to implement an algorithm that takes user-defined start and end dates for a timetable, along with a CSV file of radio astronomy observation proposals to be scheduled within that duration. The algorithm will generate PNG images for each week in that timeframe, effectively visualizing the scheduled proposals.

## System Design

### Decomposition

<div align="center">
    <img src="res/decomposition.png" alt="Decomposition" />
</div>

### Use Case

<div align="center">
    <img src="res/use-case.png" alt="Use Case" />
</div>

### User Interface

#### Home Page

<div align="center">
    <img src="res/home-page-ui.png" alt="Home Page User Interface" />
</div>

#### Generate Page

<div align="center">
    <img src="res/generate-page-ui.png" alt="Generate Page User Interface" />
</div>

### Genetic Algorithm Flow Charts

<div align="center">
    <img src="res/ga-flow-chart-1.png" alt="Genetic Algorithim Flow Chart 1" />
</div>

<div align="center">
    <img src="res/ga-flow-chart-2.png" alt="Genetic Algorithm Flow Chart 2" />
</div>

### Working Principles

<div align="center">
    <img src="res/working-principles.png" alt="" />
</div>

### Contributing

- Contributions are welcome! Please feel free to submit a pull request or open an issue.

### License

- You can use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software.

- Attribution is required when using or distributing the code.

- This software is provided 'as is without any express or implied warranty. Use at your own risk.