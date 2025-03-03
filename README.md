# Auto-Scheduler

## Description

The current manual method of scheduling radio astronomy observations at SARAO is error-prone, time-consuming, and labor-intensive. This has resulted in the underutilization of the telescopes, negatively impacting revenue. The goal of this project is to maximize the utilization of the SARAO telescopes by proposing an auto-scheduler that uses a Genetic Algorithm to schedule observations for the upcoming week without conflicts.

## File Structure

- **classes/**: Contains the class definitions used in the project.
- **venv/**: Virtual environment for Python dependencies.
- **.dockerignore**: Specifies files to ignore when building Docker images.
- **.gitignore**: Specifies files to ignore in version control.
- **Dockerfile**: Contains the instructions to build the Docker image for the project.
- **Makefile**: The main entry point for the application.
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