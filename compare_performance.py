import random
from typing import Any, Dict, List
import matplotlib.pyplot as plt
from sat_problem import *
import numpy as np
from n_queens import NQueens
from sat_solvers import GSAT, WalkSAT
from search_solution import SATSolution
from sudoku import Sudoku
import argparse


def run_trials(algorithm, problem: CNF, p=0.3, max_iterations=50000, n_trials=5, num_randomized_restarts=1) -> List[SATSolution]:
    """
    Run provided algorithm for n_trials on a given problem.

    Inputs:
        algorithm: SATAlgorithm subclass to run (GSAT or WalkSAT)
        problem: CNF to run algorithm on
        p: probability of flipping a random variable
        max_iterations: maximum number of flips to run algorithm for
        n_trials: number of trials to run
        num_randomized_restarts: number of randomized restarts to run

    Outputs:
        all_results: list of SATSolution for each trial
    """
    all_results = []
    for _ in range(n_trials):
        result = algorithm(p=p, max_iterations=max_iterations,
                           num_randomized_restarts=num_randomized_restarts).satisfy(problem)
        all_results.append(result)

    return all_results


def run_experiments(algorithm, problem, num_p=5, max_iterations=50000, n_trials=5, num_randomized_restarts=1) -> Dict[float, List[SATSolution]]:
    """
    Run experiments for a given algorithm and problem.
    Vary the probability of flipping a random variable and compile the results for each p

    Inputs:
        algorithm: SATAlgorithm subclass to run (GSAT or WalkSAT)
        problem: CNF to run algorithm on
        num_p: number of probabilities to run algorithm with
        max_iterations: maximum number of flips to run algorithm for
        n_trials: number of trials to run
        num_randomized_restarts: number of randomized restarts to run

    Outputs:
        results: dictionary of results for each p
    """
    # List of probabilities to run algorithm with
    ps = np.linspace(0, 1, num_p)
    results = {}

    # For each p, run a set of trials and compile the results together
    for p in ps:
        trial_results = run_trials(algorithm, problem, p, max_iterations,
                                   n_trials, num_randomized_restarts)
        results[p] = trial_results

    return results


def make_table_of_results(results: Dict[float, List[SATSolution]]):
    """
    Make a table of results for a given set of results (dictionary from p to list of results)

    Inputs:
        results: dictionary of results for each p

    Outputs:
        table: a list of dictionaries containing the statistics for each p
    """
    table = []

    for p, trials in results.items():
        row = {'p': p}

        # Calculate statistics for each metric
        metrics = ['runtime_seconds', 'num_iterations']
        for metric in metrics:
            values = [getattr(trial.stats, metric) for trial in trials]
            row[f'{metric}_mean'] = np.mean(values)
            row[f'{metric}_std'] = np.std(values)

        # Calculate success rate
        successes = sum(1 for trial in trials if trial.model is not None)
        row['success_rate'] = successes / len(trials)

        table.append(row)
    return table


def print_results_table(gsat_results, walksat_results):
    """
    Print a formatted table of results for both GSAT and WalkSAT algorithms

    Inputs:
        gsat_results: results from run_experiments for GSAT
        walksat_results: results from run_experiments for WalkSAT
    """
    gsat_table = make_table_of_results(gsat_results)
    walksat_table = make_table_of_results(walksat_results)
    print("### GSAT Results")
    print("| $p$ | Run Time (Average) | Run Time (Standard Dev.) | Iterations (Average) | Iterations (Standard Dev.)| Success Rate |")
    print("| --- | --- | --- | --- | --- | --- |")
    for row in gsat_table:
        print(f"| {row['p']:.2f} | {row['runtime_seconds_mean']:.2f} | {row['runtime_seconds_std']:.2f} | { row['num_iterations_mean']:.0f} | {row['num_iterations_std']:.0f} | {row['success_rate']:.2f} |")

    print("\n### WalkSAT Results")
    print("| $p$ | Run Time (Average) | Run Time (Standard Dev.) | Iterations (Average) | Iterations (Standard Dev.) | Success Rate |")
    print("| --- | --- | --- | --- | --- | --- |")
    for row in walksat_table:
        print(f"| {row['p']:.2f} | {row['runtime_seconds_mean']:.2f} | {row['runtime_seconds_std']:.2f} | { row['num_iterations_mean']:.0f} | {row['num_iterations_std']:.0f} | {row['success_rate']:.2f} |")


def clauses_satisfied_per_iteration(results, algorithm_name=''):
    """
    Make plot of number of clauses satisfied per iteration for a given set of results

    Inputs:
        results: results from run_experiments
        algorithm_name: name of algorithm (for saving plot)
    """

    plt.clf()
    fig, ax = plt.subplots(figsize=(10, 6))
    for p in results:
        trials = results[p]
        satisfied_clauses = [trial.stats.num_unsatisfied_clauses for trial in trials]
        longest_run = max([len(x) for x in satisfied_clauses])
        for num_sat in satisfied_clauses:
            num_sat.extend([0] * (longest_run - len(num_sat)))

        all_trials = np.array(satisfied_clauses)
        average = all_trials.mean(axis=0)
        ax.plot(average, label=f'p={p:.2f}')

    ax.set_ylabel('Number of Unsatisfied Clauses')
    ax.set_xlabel('Number of Iterations')
    ax.set_yscale('log')

    # Move legend outside the plot
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    # Adjust layout to prevent cutting off the legend
    plt.tight_layout()

    plt.savefig(
        f'{algorithm_name}_clauses_satisfied_per_iteration.png', bbox_inches='tight')
    plt.close(fig)


def iterations_vs_time_plot(results_gsat, results_walksat):
    """
    Make plot of iterations vs time for GSAT and WalkSAT

    Inputs:
        results_gsat: results from GSAT (see run_experiments)
        results_walksat: results from WalkSAT (see run_experiments)
    """
    plt.clf()
    fig, ax = plt.subplots(figsize=(10, 6))  # Increase figure size

    all_runtimes = []
    all_iterations = []
    for p in results_gsat:
        for trial in results_gsat[p]:
            all_runtimes.append(trial.stats.runtime_seconds)
            all_iterations.append(trial.stats.num_iterations)

    walksat_runtimes = []
    walksat_iterations = []
    for p in results_walksat:
        for trial in results_walksat[p]:
            walksat_runtimes.append(trial.stats.runtime_seconds)
            walksat_iterations.append(trial.stats.num_iterations)

    print(len(all_iterations), len(all_runtimes))
    print(len(walksat_iterations), len(walksat_runtimes))

    ax.scatter(all_iterations, all_runtimes, label='GSAT')
    ax.scatter(walksat_iterations, walksat_runtimes, label='WalkSAT')

    ax.set_xlabel('Number of Iterations')
    ax.set_ylabel('Runtime (seconds)')

    # Move legend outside the plot
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    # Adjust layout to prevent cutting off the legend
    plt.tight_layout()

    plt.savefig('iterations_vs_time.png', bbox_inches='tight')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="Compare performance of SAT solvers on N-Queens and Sudoku.")
    parser.add_argument("--num_trials", type=int, default=1,
                        help="Number of trials to run (default: 1)")
    parser.add_argument("--randomized_restarts", type=int, default=1,
                        help="Number of randomized restarts to run (default: 1)")
    parser.add_argument("--max_iterations", type=int, default=10000,
                        help="Maximum number of iterations/flips (default: 10000)")
    parser.add_argument("-n", type=int, default=8,
                        help="Size of the N-Queens problem (default: 8)")
    parser.add_argument("--puzzle", type=str, default='sudoku',
                        help="Type of problem to solve (sudoku or queens)")
    parser.add_argument("--num_p", type=int, default=11,
                        help="Number of probabilities to run algorithm with (default: 11)")
    args = parser.parse_args()

    if args.puzzle == 'sudoku':
        simple_board = [
            [1, 0, 3, 0],
            [0, 0, 0, 0],
            [4, 0, 0, 0],
            [0, 0, 0, 0]
        ]
        problem = Sudoku(simple_board).compile()
    elif args.puzzle == 'queens':
        problem = NQueens(args.n).compile()
    else:
        raise ValueError("Invalid puzzle type. Choose 'sudoku' or 'queens'.")

    # Example simple Sudoku board for testing

    results = run_experiments(GSAT, problem, num_p=args.num_p, n_trials=args.num_trials,
                              max_iterations=args.max_iterations, num_randomized_restarts=args.randomized_restarts)
    clauses_satisfied_per_iteration(results, 'GSAT')

    walksat_results = run_experiments(WalkSAT, problem, num_p=args.num_p, n_trials=args.num_trials,
                                      max_iterations=args.max_iterations, num_randomized_restarts=args.randomized_restarts)
    clauses_satisfied_per_iteration(walksat_results, 'WalkSAT')
    iterations_vs_time_plot(results, walksat_results)
    print_results_table(results, walksat_results)


if __name__ == '__main__':
    main()
