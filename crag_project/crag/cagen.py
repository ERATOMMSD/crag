"""
This module provides CAgenTestSuiteGenerator to extend TestSuiteGenerator
to be able to use CAgen tool as a backend.
"""

from . import tsgenerator as tsgen
from . import utils
import random as ra

def index_str_to_int(index_str, possible_indices):
    """Convert string to integer, while also taking account unspecified values."""
    if index_str in possible_indices:
        return int(index_str)
    else:
        return int(ra.choice(possible_indices))

def parse_cagen_command_result(cagen_command_result, possible_indices):
    """Parses cagen command result string into a list of lists of ints."""
    start_line = 0
    return [[index_str_to_int(index_str, possible_indices) for index_str in line.split(",")] for line in cagen_command_result.splitlines()[start_line:]]


"""This class extends TestSuiteGenerator for CAgen backend."""
class CAgenTestSuiteGenerator(tsgen.TestSuiteGenerator):
    def __init__(self,
                 cagen_executable_filepath,
                 input_filepath,
                 output_filepath):
        super().__init__()
        self.cagen_executable_filepath = cagen_executable_filepath
        self.input_filepath = input_filepath
        self.output_filepath = output_filepath

    def call_with_seed(self, strength, seed_test_suite):
        """Calls CAgen with given strength and seed test suite. Notice
        that the model is described in the input file which includes
        the seed test suite definition. The result of CAgen
        is the output file."""
        self.create_input_file(seed_test_suite)
        utils.call_command(
            f"{self.cagen_executable_filepath} -t {strength} -i {self.input_filepath} -o {self.output_filepath}")
        with open(self.output_filepath) as f:
            possible_indices = [str(index) for index in range(self.param_value_count)]
            return parse_cagen_command_result(f.read(), possible_indices)

    def call(self, strength):
        """Calls CAgen with given strength. Notice that the model is
        described in the input file. The result of CAgen is the output file."""
        return self.call_with_seed(strength, None)

    def create_input_file(self, seed_test_suite=None):
        """This method creates an input file. The model and seeds are passed
        to CAgen via an input file."""
        lines = ["[System]", "Name: CRAG", "",
                 "[Parameter]", self.typed_model_string, ""]
        if seed_test_suite is not None:
            lines += ["[Test Set]", self.get_seed_string(seed_test_suite, ",")]

        with open(self.input_filepath, "w") as f:
            f.write("\n".join(lines))


if __name__ == "__main__":
    ctsg = CAgenTestSuiteGenerator("./fipo-cli", "CAgenInput.txt", "CAgenOutput.txt")
    ctsg.set_model(5, 5)
    print(len(ctsg.call(2)))
