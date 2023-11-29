from . import tsgenerator as tsgen
from . import utils


def parse_acts_command_result(acts_command_result):
    start_line = utils.line_index(acts_command_result, "Length0") + 1
    return [[int(index_str) for index_str in line.split(",")] for line in acts_command_result.splitlines()[start_line:]]


class ACTSTestSuiteGenerator(tsgen.TestSuiteGenerator):
    def __init__(self,
                 java_executable_filepath,
                 acts_jar_filepath,
                 input_filepath,
                 output_filepath):
        super().__init__()
        self.java_executable_filepath = java_executable_filepath
        self.acts_jar_filepath = acts_jar_filepath
        self.input_filepath = input_filepath
        self.output_filepath = output_filepath

    def call_with_seed(self, strength, seed_test_suite):
        self.create_input_file(seed_test_suite)
        utils.call_command(
            f"{self.java_executable_filepath} -Ddoi={strength} -Doutput=csv -Dmode=extend -jar {self.acts_jar_filepath} {self.input_filepath} {self.output_filepath}")
        with open(self.output_filepath) as f:
            return parse_acts_command_result(f.read())

    def call(self, strength):
        self.create_input_file()
        utils.call_command(
            f"{self.java_executable_filepath} -Ddoi={strength} -Doutput=csv -Dmode=scratch -jar {self.acts_jar_filepath} {self.input_filepath} {self.output_filepath}")
        with open(self.output_filepath) as f:
            return parse_acts_command_result(f.read())

    def create_input_file(self, seed_test_suite=None):
        lines = ["[System]", "Name: CRAG", "",
                 "[Parameter]", self.typed_model_string, ""]
        if seed_test_suite is not None:
            lines += ["[Test Set]", self.get_seed_string(seed_test_suite, ",")]

        with open(self.input_filepath, "w") as f:
            f.write("\n".join(lines))


if __name__ == "__main__":
    atsg = ACTSTestSuiteGenerator("java", "acts_3.2.jar", "ACTSInput.txt", "ACTSOutput.txt")
    atsg.set_model(5, 5)
    print(len(atsg.call(2)))
