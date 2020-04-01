import os
import xml.etree.ElementTree as ET
from .config import Config


class ProblemManager:
    def __init__(self, problem_id):
        self.problem_id = problem_id
        self.package_path = os.path.join(Config.PROBLEMS_PATH, str(self.problem_id).zfill(6))
        self.xml_path = os.path.join(self.package_path, 'problem.xml')

        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        self.names = root.find('names')
        self.statements = root.find('statements')
        testset = root.find('judging')[0]
        self.time_limit_ms = int(testset.find('time-limit').text)
        self.memory_limit_kb = int(testset.find('memory-limit').text) // 1024
        self.test_count = int(testset.find('test-count').text)
        self.input_path_pattern = os.path.join(self.package_path, testset.find('input-path-pattern').text)
        self.output_path_pattern = os.path.join(self.package_path, testset.find('answer-path-pattern').text)
        checker_source = root.find('assets').find('checker').find('source')
        self.testlib_path = os.path.join(self.package_path, 'files', 'testlib.h')
        self.checker_source_path = os.path.join(self.package_path, checker_source.attrib['path'])
        self.checker_binary_path = os.path.join(self.package_path, 'check.out')
        self.checker_language = self.match_language(checker_source.attrib['type'])

    def name(self, language):
        for child in self.names:
            if child.attrib['language'] == language:
                return child.attrib['value']

    def statement_path(self, language, tp):
        for child in self.statements:
            if child.attrib['type'] == tp:
                return os.path.join(self.package_path, child.attrib['path'])

    def test_input_path(self, test_number):
        return self.input_path_pattern % test_number

    def test_output_path(self, test_number):
        return self.output_path_pattern % test_number

    @staticmethod
    def match_language(language):
        if language.startswith('cpp'):
            return 'cpp'
        elif language.startswith('py'):
            return 'py'
