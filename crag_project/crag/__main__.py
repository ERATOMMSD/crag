"""This is the main entry point of the CRAG standalone executable."""

from . import roadgeometry as rg
from . import crag
import argparse
import json
import sys

def setup_parser():
    """Setup command line interface argument parser."""
    parser = argparse.ArgumentParser(description="CRAG cli tool")

    # CORE PARAMETER arguments
    parser.add_argument("--use-seed", type=bool, default=True,
                        help="Use generated tests of previous strength as seeds or not.")
    parser.add_argument("--seed-best", type=bool, default=True,
                        help="When preparing seeds take only the best tests.")
    parser.add_argument("--best-ratio", type=float, default=0.1,
                        help="Percentage of top scoring tests taken as seed.")
    parser.add_argument("--resample", type=bool, default=True,
                        help="Whether to resample and run the test (for evaluation) even if it was evaluated before.")
    parser.add_argument("--fitness-aggregation-method", choices=['minimum', 'average', 'first'], default='average',
                        help="When a test is rerun for evaluation, how to aggregate available fitness values.")
    parser.add_argument("--max-strength", type=int, default=5,
                        help="Maximum strength for combinatorial test generation.")

    # ROAD GEOMETRY arguments
    parser.add_argument("--road-section-count", type=int, default=5,
                        help="How many sections each generated road should have.")
    parser.add_argument("--param-value-count", type=int, default=5,
                        help="How many values length and kappa parameters in a section has.")
    parser.add_argument("--max-road-scalar", type=float, default=1.2,
                        help="The scalar for the ratio of maximum road length to map size.")
    parser.add_argument("--min-road-scalar", type=float, default=0.6,
                        help="The scalar for the ration of minimum road length to map size.")
    parser.add_argument("--lane-width", type=float, default=10,
                        help="The width of lane in units consistent with map size.")
    parser.add_argument("--map-size", type=float, default=200,
                        help="Edge length of a square map to be considered for road generation.")
    parser.add_argument("--min-radius", type=float, default=15,
                        help="Threshold in units consistent with map size for sharpness of generated roads.")

    # BACKEND arguments
    parser.add_argument("--backend", choices=["pict", "acts", "cagen"], default="pict",
                        help="Backend used for combinatorial test generation for given strength and seeds.")

    # ACTS-specific arguments
    parser.add_argument("--acts-java-executable-filepath", type=str, default="java",
                        help="Java executable filepath as needed by ACTS.")
    parser.add_argument("--acts-jar-path", type=str, default="acts_3.2.jar",
                        help="Filepath of jar file for ACTS.")
    parser.add_argument("--acts-input-filepath", type=str, default="ACTSInput.txt",
                        help="Filepath for input to be used in ACTS.")
    parser.add_argument("--acts-output-filepath", type=str, default="ACTSOutput.txt",
                        help="Filepath for output to be used in ACTS.")

    # CAgen-specific arguments
    parser.add_argument("--cagen-executable-filepath", type=str, default="java",
                        help="CAgen (fipo-cli) executable filepath as needed by CAgen.")
    parser.add_argument("--cagen-input-filepath", type=str, default="CAgenInput.txt",
                        help="Filepath for input to be used in CAgen.")
    parser.add_argument("--cagen-output-filepath", type=str, default="CAgenOutput.txt",
                        help="Filepath for output to be used in CAgen.")

    # PICT-specific arguments
    parser.add_argument("--pict-executable-filepath", type=str, default="pict",
                        help="Filepath for the executable of PICT.")
    parser.add_argument("--pict-model-filepath", type=str, default="PICTModel.txt",
                        help="Filepath for the model to be used in PICT.")
    parser.add_argument("--pict-seed-filepath", type=str, default="PICTSeed.txt",
                        help="Filepath for the seeds to be used in PICT.")

    return parser


def get_evaluate_and_budget_availability_functions():
    """Communication with CRAG cli is over standard input and output. """
    crag_state = {"budget_available": True}

    def evaluate_function(road):
        road_str = json.dumps(road)
        print(road_str, file=sys.stdout, flush=True)
        line = sys.stdin.readline().strip()
        arr = json.loads(line)
        if len(arr) > 1:
            if arr[-1] == "EXIT":
                crag_state["budget_available"] = False
        return arr

    def budget_availability_function():
        return crag_state["budget_available"]

    return evaluate_function, budget_availability_function


def main():
    parser = setup_parser()
    args = parser.parse_args()

    core_params = {"use_seed": args.use_seed, "seed_best": args.seed_best, "best_ratio": args.best_ratio,
                   "rerun": args.rerun, "fitness_aggregation_method": args.fitness_aggregation_method,
                   "max_strength": args.max_strength}

    geometry_params = {"road_section_count": args.road_section_count, "param_value_count": args.param_value_count,
                       "max_road_scalar": args.max_road_scalar, "min_road_scalar": args.min_road_scalar,
                       "lane_width": args.lane_width, "map_size": args.map_size, "min_radius": args.min_radius}

    if args.backend == "acts":
        from . import acts
        tsg = acts.ACTSTestSuiteGenerator(args.acts_java_executable_filepath,
                                          args.acts_jar_filepath,
                                          args.acts_input_filepath,
                                          args.acts_output_filepath)
    elif args.backend == "cagen":
        from . import cagen
        tsg = cagen.CAgenTestSuiteGenerator(args.cagen_executable_filepath,
                                            args.cagen_input_filepath,
                                            args.cagen_output_filepath)
    else: # pict
        from . import pict
        tsg = pict.PictTestSuiteGenerator(args.pict_executable_filepath,
                                          args.pict_model_filepath,
                                          args.pict_seed_filepath)

    evaluate_function, budget_availability_function = get_evaluate_and_budget_availability_functions()

    crag1 = crag.CRAG(core_params, geometry_params, tsg, evaluate_function, budget_availability_function)
    crag1.generate()


main()
