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

### Genetic Algorithim Flow Charts

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

## File Structure

- **classes/**: Contains the class definitions used in the project.
- **outputs/**: Contains the .PNG output images of the generated weakly timetable.
- **proposals/csv**: Contains the excel spreadsheet of proposals (excluded from git).
- **res/**: Contains README.md file images.
- **tests/**: Contains the pytest unit tests for this project.
- **venv/**: Virtual environment for Python dependencies (excluded from git).
- **.dockerignore**: Specifies files to ignore when building Docker images.
- **.gitignore**: Specifies files to ignore in version control.
- **Dockerfile**: Contains the instructions to build the Docker image for the project.
- **docker-compose.yaml**: Defines Docker continers configuration.
- **main.py**: The main entry point for the application.
- **Makefile**: Defines the custom CLI cmd for automate admin task of the project.
- **README.md**: This project description file.
- **requirements.txt**: Lists the dependencies required for the project.

## Cloning the Project

To clone the project, run the following command in your terminal:

```git clone https://github.com/ska-sa/genetic-algorithm-auto-scheduler```

Make sure you are within the project folder, if not. Then use:

```cd genetic-algorithm-auto-scheduler```

## Addin the CSV FileCreate new directory:

```mkdir -p proposals/csv```

Please download the sensitive CSV file from [Proposals CSV File](https://drive.google.com/file/d/1uKx0ocyvraKuRoVFqLJ_8v3jRMwQrhCL/view).


Move the downloaded CSV file in the `proposals/csv` directory.

Rename the file to `ObsList1737538994939.csv`

## Running the Code

### Using Virtual Environment

To setup virtual environemnts:

```python -m virtualenv venv```

To activate virtual environemnt:

```. venv/bin/activate```

To install dependecies:

```venv/bin/python -m pip install -r requirements.txt```

To run the main script:

```venv/bin/python main-v2.py```

After sucesfuly runnig executing the main script the output image can be found here `outputs/'week 02-09-2025 to 02-15-2025 timetable.png'`

### Using Docker

To build a docker image:

```docker build -t genetic-algorithm-auto-scheduler .```

To run the docker image:

```docker run genetic-algorithm-auto-scheduler```

To build an image using docker-compose:

```docker-compose build```

To start the container using docker-compose:

```docker-compose up```

To stop the container using docker-compose:

```docker-compose down```

### Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

### License

- You can use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.
- Attribution is required when using or distributing the code.
- This software is provided 'as is', without any express or implied warranty. Use at your own risk.