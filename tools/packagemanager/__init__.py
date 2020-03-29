import os
from .config import Config


class ProblemManager:
    def __init__(self, problem_id):
        self.problem_id = problem_id
        self.package_path = os.path.join(Config.PROBLEMS_PATH, str(self.problem_id).zfill(6))
        self.checker_source = os.path.join(self.package_path, 'check.cpp')
        self.checker_binary = os.path.join(self.package_path, 'check.out')
        self.tests_input_path = os.path.join(self.package_path, 'tests')
        self.tests_output_path = os.path.join(self.package_path, 'tests')
        self.time_limit_ms = 1000
        self.memory_limit_kb = 262144

    def number_of_tests(self):
        return len(os.listdir(self.tests_input_path)) // 2

    def test_input_file(self, test_number):
        return os.path.join(self.tests_input_path, str(test_number).zfill(2))

    def test_output_file(self, test_number):
        return os.path.join(self.tests_output_path, str(test_number).zfill(2) + '.a')
