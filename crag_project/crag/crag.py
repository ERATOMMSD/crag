import math
from . import roadgeometry as rg
from . import utils


class CRAG:
    """Combinatorial testing-based RoAd Generator"""

    def __init__(self, core_params, geometry_params, test_suite_generator,
                 evaluate_function, budget_availability_function):
        self.use_seed = core_params["use_seed"] # True/False
        self.seed_best = core_params["seed_best"] # True/False (Seed whole if False)
        self.best_ratio = core_params["best_ratio"] # [0,1]
        self.rerun = core_params["rerun"] # True/False
        self.fitness_aggregation_method = core_params["fitness_aggregation_method"]
        self.max_strength = core_params["max_strength"]

        self.road_section_count = geometry_params["road_section_count"]
        self.param_value_count = geometry_params["param_value_count"]
        self.max_road_scalar = geometry_params["max_road_scalar"]
        self.min_road_scalar = geometry_params["min_road_scalar"]
        self.lane_width = geometry_params["lane_width"]
        self.map_size = geometry_params["map_size"]
        self.min_radius = geometry_params["min_radius"]

        # N-gon approach:
        # The road is composed of many small segments that are straight
        # self.ds represents the length of those segments
        # We start with a circle of radius R. Then we approximate it with an
        # N-gon. The edge length determines self.ds

        R = self.min_radius
        N = 70 # Constant utilized in (Arcaini & Cetinkaya, SBFT, 2023).
        self.ds = 2 * R * math.sin(math.pi / N)

        # Maximum length of a generated road
        self.max_road_length = self.map_size * self.max_road_scalar
        # Maximum count of pieces in one section of a road
        self.max_segment_count = int((self.max_road_length / self.road_section_count) / self.ds)

        # Minimum length of a generated road
        self.min_road_length = self.map_size * self.min_road_scalar
        # Minimum count of pieces in one section of a road
        self.min_segment_count = int((self.min_road_length / self.road_section_count) / self.ds)

        # We use the formula kappa = 1 / min_radius to find the maximum
        # allowable curvature so that road radius values are larger than min_radius.
        # Here, we follow the N-gon approximation approach, and
        # find the maximum allowable curvature using self.ds and N.
        # This gives accurate results when combined with the numerical
        # integration in frenet_to_cartesian calculations.
        self.global_curvature_bound = 2 * math.pi / (N * self.ds)  # Maximum of the absolute value of curvature

        self.test_suite_generator = test_suite_generator
        self.test_suite_generator.set_model(self.road_section_count, self.param_value_count)

        # Function that evaluates the effectiveness of a road
        self.evaluate_function = evaluate_function

        # Function that indicates availability of budget in execution of crag
        self.budget_availability_function = budget_availability_function

        self.fitness_dictionary = {}

    def generate_roads(self, test_suite):
        roads = []
        for test in test_suite:
            lengths_indices = test[:self.road_section_count]
            kappas_indices = test[self.road_section_count:]

            road = rg.generate_road_with_reframability_check(lengths_indices, kappas_indices,
                                                             self.param_value_count,
                                                             self.min_segment_count, self.max_segment_count,
                                                             self.global_curvature_bound, self.ds,
                                                             self.lane_width, self.map_size)

            roads.append(road)

        return roads

    def best_tuples(self, test_suite, evaluations):
        fitness_values = []
        for index, test in enumerate(test_suite):
            if self.fitness_aggregation_method == "average":
                utils.update_average(self.fitness_dictionary, test, evaluations[index][0])
            elif self.fitness_aggregation_method == "minimum":
                utils.update_minimum(self.fitness_dictionary, test, evaluations[index][0])
            else: # In other words: self.fitness_aggregation_method == "first"
                utils.update_first(self.fitness_dictionary, test, evaluations[index][0])
            fitness_values.append(self.fitness_dictionary[tuple(test)])

        if self.seed_best:
            return utils.take_best(test_suite, lambda i: fitness_values[i], int(len(test_suite) * self.best_ratio))
        else:
            return test_suite

    def filter(self, test_suite, strength, seed_test_suite):
        test_suite = [test for test in test_suite if utils.has_m_match(test, seed_test_suite, strength - 1)]
        return test_suite

    def generate(self):
        all_roads_and_evaluations = []
        evaluation_dict = {}
        while True:
            strength = 2
            test_suite = self.test_suite_generator.generate_test_suite(strength)
            roads = self.generate_roads(test_suite)
            # Evaluate
            evaluations = []
            budget_over = False
            for (test, road) in zip(test_suite, roads):
                evaluation = self.evaluate_function(road)
                if not self.budget_availability_function():
                    budget_over = True
                    break
                evaluations.append(evaluation)
                evaluation_dict[tuple(test)] = evaluation
                all_roads_and_evaluations.append((road, evaluation))
            if budget_over:
                break
            for strength in range(3, self.max_strength + 1):
                if self.use_seed:
                    seed_test_suite = self.best_tuples(test_suite, evaluations)
                    test_suite = self.test_suite_generator.generate_test_suite(strength, seed_test_suite)
                    test_suite = self.filter(test_suite, strength, seed_test_suite)
                else:
                    test_suite = self.test_suite_generator.generate_test_suite(strength)
                roads = self.generate_roads(test_suite)
                # Evaluate
                evaluations = []
                for (test, road) in zip(test_suite, roads):
                    if (not self.rerun) and self.use_seed and (tuple(test) in evaluation_dict):
                        evaluation = evaluation_dict[tuple(test)]
                    else:
                        evaluation = self.evaluate_function(road)
                    if not self.budget_availability_function():
                        budget_over = True
                        break
                    evaluations.append(evaluation)
                    evaluation_dict[tuple(test)] = evaluation
                    all_roads_and_evaluations.append((road, evaluation))

                if budget_over:
                    break
            if budget_over:
                break
        return all_roads_and_evaluations


if __name__ == "__main__":
    core_params = {}
    core_params["use_seed"] = True
    core_params["seed_best"] = True
    core_params["best_ratio"] = True
    core_params["rerun"] = True
    core_params["fitness_aggregation_method"] = "minimum"
    core_params["max_strength"] = 5

    geometry_params = {}
    geometry_params["road_section_count"] = 5
    geometry_params["param_value_count"] = 5
    geometry_params["max_road_scalar"] = 1.2
    geometry_params["min_road_scalar"] = 0.6
    geometry_params["lane_width"] = 10
    geometry_params["map_size"] = 200
    geometry_params["min_radius"] = 15

    import acts

    atsg = acts.ACTSTestSuiteGenerator("java", "acts_3.2.jar", "ACTSInput.txt", "ACTSOutput.txt")

    def evaluate_function(road):
        (road_points, is_in_map, is_reframable) = road
        if (not is_in_map) and (not is_reframable):
            return [100]

            # Check self-intersections and reframe if possible
        if rg.is_likely_self_intersecting(road_points, geometry_params["lane_width"]):
            return [100]

        if not is_reframable:
            return [100]

        # Let's try to find roads that have small ending x coordinates
        return [road_points[-1][0]]

    def get_budget_availability_function():
        iterations = 10
        def budget_availability_function():
            nonlocal iterations
            iterations -= 1
            return iterations >= 0

        return budget_availability_function

    crag = CRAG(core_params, geometry_params, atsg, evaluate_function, get_budget_availability_function())
    crag.generate()



