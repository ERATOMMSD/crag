from . import tsgenerator as tsgen
from . import utils


def parse_pict_command_result(pict_command_result):
    with open("/tmp/test.txt", "a") as f:
        f.write(pict_command_result)
    start_line = utils.line_index(pict_command_result, "Length0") + 1
    return [[int(index_str) for index_str in line.split()] for line in pict_command_result.splitlines()[start_line:]]


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
        super().set_model(road_section_count, param_value_count)
        self.create_model()

    def call_with_seed(self, strength, seed_test_suite):
        self.write_to_seed_file(self.get_seed_string(seed_test_suite, "\t"))
        pict_command_result = utils.call_command(
            f"{self.pict_executable_filepath} {self.model_filepath} /r /o:{strength} /e:{self.seed_filepath}")
        return parse_pict_command_result(pict_command_result)

    def call(self, strength):
        pict_command_result = utils.call_command(f"{self.pict_executable_filepath} {self.model_filepath} /r")
        return parse_pict_command_result(pict_command_result)

    def create_model(self):
        with open(self.model_filepath, "w") as f:
            f.write(self.model_string)

    def write_to_seed_file(self, seed_string):
        with open(self.seed_filepath, "w") as f:
            f.write(seed_string)


if __name__ == "__main__":
    ptsg = PictTestSuiteGenerator(utils.get_fullpath("pict"), "PICTModel.txt", "PICTSeed.txt")
    ptsg.set_model(5, 5)
    print(len(ptsg.call(2)))
