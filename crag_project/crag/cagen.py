from . import tsgenerator as tsgen
from . import utils
import random as ra

def index_str_to_int(index_str, possible_indices):
    if index_str in possible_indices:
        return int(index_str)
    else:
        return int(ra.choice(possible_indices))

def parse_cagen_command_result(acts_command_result, possible_indices):
    start_line = 0
    return [[index_str_to_int(index_str, possible_indices) for index_str in line.split(",")] for line in acts_command_result.splitlines()[start_line:]]


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
        self.create_input_file(seed_test_suite)
        utils.call_command(
            f"{self.cagen_executable_filepath} -t {strength} -i {self.input_filepath} -o {self.output_filepath}")
        with open(self.output_filepath) as f:
            possible_indices = [str(index) for index in range(self.param_value_count)]
            return parse_cagen_command_result(f.read(), possible_indices)

    def call(self, strength):
        return self.call_with_seed(strength, None)

    def create_input_file(self, seed_test_suite=None):
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
