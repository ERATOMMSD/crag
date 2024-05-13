import math
import random

from jmetal.core.problem import Problem, S
from jmetal.core.solution import FloatSolution
from jmetal.util.termination_criterion import StoppingByEvaluations
from jmetal.core.operator import Mutation
from jmetal.algorithm.singleobjective.evolution_strategy import EvolutionStrategy
from abc import ABC

import crag.roadgeometry as rg


class RoadConfigurationProblem(Problem[FloatSolution], ABC):
    def __init__(self, road_section_count, length_min, length_max, kappa_min, kappa_max, ds, lane_width, map_size, road_evaluate_function):
        super(RoadConfigurationProblem, self).__init__()
        self.road_section_count = road_section_count
        self.length_min = length_min
        self.length_max = length_max
        self.kappa_min = kappa_min
        self.kappa_max = kappa_max
        self.ds = ds
        self.lane_width = lane_width
        self.map_size = map_size
        self.road_evaluate_function = road_evaluate_function
        self.lower_bounds = []
        self.upper_bounds = []
        for i in range(self.road_section_count):
            self.lower_bounds.append(self.length_min[i])
            self.upper_bounds.append(self.length_max[i])
        for i in range(self.road_section_count):
            self.lower_bounds.append(self.kappa_min[i])
            self.upper_bounds.append(self.kappa_max[i])

    def number_of_variables(self) -> int:
        return len(2 * self.road_section_count)

    def create_solution(self) -> FloatSolution:
        new_solution = FloatSolution(
            self.lower_bounds, self.upper_bounds,
            1,
            0
        )

        new_solution.variables = [random.uniform(self.lower_bounds[i], self.upper_bounds[i]) for i in range(self.number_of_variables()) ]

        return new_solution

    def evaluate(self, solution: FloatSolution):
        x0 = 0
        y0 = 0
        theta0 = random.uniform(0, 2 * math.pi)
        segment_counts = [int(i / self.ds) for i in solution.variables[0:self.road_section_count]]
        kappas = []
        for i in range(len(segment_counts)):
            segment_count = segment_counts[i]
            kappa = random.uniform(self.kappa_min, self.kappa_max)
            kappas += [kappa for j in range(segment_count)]
        road = rg.frenet_to_cartesian_road_points_with_reframability_check(x0, y0, theta0, self.ds, kappas, self.lane_width, self.map_size)
        solution.objectives[0] = self.evaluate_function(solution.variables)


def get_best_road_and_evaluation(road_section_count, length_min, length_max, kappa_min, kappa_max, ds, lane_width, map_size, evaluate_function):
    algorithm = EvolutionStrategy(problem=RoadConfigurationProblem(road_section_count, length_min, length_max, kappa_min, kappa_max, ds, lane_width, map_size, evaluate_function),
                                  mu=1,
                                  lambda_=1,
                                  elitist=True,
                                  mutation=Mutation(1.0),
                                  termination_criterion=StoppingByEvaluations(max_evaluations=5))
    algorithm.run()
    best_solution = algorithm.get_result()[0]
    best_road = best_solution.variables
    best_evaluation = best_solution.objectives[0]
    return (best_road, best_evaluation)

