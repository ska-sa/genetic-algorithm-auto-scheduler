from pathlib import Path
import typer
from generic_algorithm import GenericAlgorithm
from individual import Individual
from util import read_observation_list_file

app = typer.Typer()

@app.command()
def run(
    num_of_individuals: int = typer.Option(50, help="Number of individuals in the population"),
    generations: int = typer.Option(100, help="Number of generations to run"),
    heuristics_combination_length: int = typer.Option(3, help="Number of heuristics combination length"),
    data_file: str = typer.Option(..., help="Path to observation list file (CSV)")
):
    """Run the genetic algorithm with specified parameters."""
    typer.echo(f"Running GA with population={num_of_individuals}, generations={generations},  heuristics={heuristics_combination_length}, data={data_file}")
    data = read_observation_list_file(Path(data_file))

    ga = GenericAlgorithm(num_of_individuals=num_of_individuals, max_generations=generations, 
                          heuristics_combination_length=heuristics_combination_length)
    best = ga.evolve_population(observation_list=data)

    print("==========================")
    print(f"Best individual in a population: Fitness{best._fitness}")
    print(f"Best individual in a population: DNA{best._dna}")
    print("==========================")
    ga.plot_graph(save_path="training_graph.png")

if __name__ == "__main__":
    app()