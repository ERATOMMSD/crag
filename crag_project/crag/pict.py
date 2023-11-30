"""
This module provides PICTTestSuiteGenerator to extend TestSuiteGenerator
to be able to use PICT tool as a backend.
"""

from . import tsgenerator as tsgen
from . import utils


def parse_pict_command_result(pict_command_result):
    """Parses pict command result string into a list of lists of ints.
    The main result of pict starts after several lines. Therefore, this
    method first figures out the start_line."""
    start_line = utils.line_index(pict_command_result, "Length0") + 1
    return [[int(index_str) for index_str in line.split()] for line in pict_command_result.splitlines()[start_line:]]


"""This class extends TestSuiteGenerator for PICT backend."""
class PictTestSuiteGenerator(tsgen.TestSuiteGenerator):
    def __init__(self,
                 pict_executable_filepath,
                 model_filepath,
                 seed_filepath):
        super().__init__()
        self.pict_executable_filepath = pict_executable_filepath
        self.model_filepath = model_filepath
        self.seed_filepath = seed_filepath

    def set_model(self, road_section_count, param_value_count):
        """This method initiates model creation, since PICT requires
        a specific model file to be created."""
        super().set_model(road_section_count, param_value_count)
        self.create_model()

    def call_with_seed(self, strength, seed_test_suite):
        """Calls PICT with given strength and seed test suite.
        Notice that the model is described in the model file and
        seed test suite is described in the seed file.
        The result of PICT is read from standard output."""
        self.write_to_seed_file(self.get_seed_string(seed_test_suite, "\t"))
        pict_command_result = utils.call_command(
            f"{self.pict_executable_filepath} {self.model_filepath} /r /o:{strength} /e:{self.seed_filepath}")
        return parse_pict_command_result(pict_command_result)

    def call(self, strength):
        """Calls PICT with given strength. Notice that the model is
        described in the model file. The result of PICT is read from
        standard output."""
        pict_command_result = utils.call_command(f"{self.pict_executable_filepath} {self.model_filepath} /r")
        return parse_pict_command_result(pict_command_result)

    def create_model(self):
        """Prepares model file required for pict."""
        with open(self.model_filepath, "w") as f:
            f.write(self.model_string)

    def write_to_seed_file(self, seed_string):
        """Writes seed test suite to seed file required for pict."""
        with open(self.seed_filepath, "w") as f:
            f.write(seed_string)


if __name__ == "__main__":
    ptsg = PictTestSuiteGenerator(utils.get_fullpath("pict"), "PICTModel.txt", "PICTSeed.txt")
    ptsg.set_model(5, 5)
    print(len(ptsg.call(2)))
