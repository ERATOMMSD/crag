from abc import abstractmethod
from . import utils


class TestSuiteGenerator:
    def __init__(self):
        # default values that can be changed with set_model
        self.road_section_count = None
        self.param_value_count = None
        self.model_string = None
        self.typed_model_string = None

    # This method can be extended if the model is to be written to a file
    def set_model(self, road_section_count, param_value_count):
        self.road_section_count = road_section_count
        self.param_value_count = param_value_count
        self.model_string = self.get_model_string()
        self.typed_model_string = self.get_model_string(with_type=True)

    def get_model_string(self, with_type=False):
        lines = []
        type_str = "(int)" if with_type else ""
        for i in range(self.road_section_count):
            lines.append(f"Length{i}{type_str}: " + ", ".join([str(j) for j in range(self.param_value_count)]))
        for i in range(self.road_section_count):
            lines.append(f"Kappa{i}{type_str}: " + ", ".join([str(j) for j in range(self.param_value_count)]))
        return "\n".join(lines)

    def get_seed_string(self, seed_test_suite, separator):
        first_line = separator.join([f"Length{i}" for i in range(self.road_section_count)]
                                    + [f"Kappa{i}" for i in range(self.road_section_count)])
        lines = [first_line] + [separator.join([str(v) for v in test]) for test in seed_test_suite]
        return "\n".join(lines)

    @abstractmethod
    def call_with_seed(self, strength, seed_test_suite):
        pass

    @abstractmethod
    def call(self, strength):
        pass

    def generate_test_suite(self, strength, seed_test_suite = None):
        if seed_test_suite is not None and len(seed_test_suite) == 0:
            seed_test_suite = None

        test_suite = self.call(strength) if seed_test_suite is None else self.call_with_seed(strength, seed_test_suite)
        return test_suite


