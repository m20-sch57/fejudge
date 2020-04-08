import os
import xml.etree.ElementTree as ET
from .config import Config


class ProblemManager:
    def __init__(self, problem_id):
        self.problem_id = problem_id
        self.package_path = os.path.join(Config.PROBLEMS_PATH, str(self.problem_id))
        self.xml_path = self.build_path('problem.xml')

        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        self.names = dict()
        for child in root.find('names'):
            self.names[child.attrib['language']] = child.attrib['value']
        self.statements_html_dir = dict()
        self.statements_pdf_dir = dict()
        for child in root.find('statements'):
            statements_dir = os.path.abspath(os.path.dirname(self.build_path(child.attrib['path'])))
            if child.attrib['type'] == 'text/html':
                self.statements_html_dir[child.attrib['language']] = statements_dir
            elif child.attrib['type'] == 'application/pdf':
                self.statements_pdf_dir[child.attrib['language']] = statements_dir

        testset = root.find('judging')[0]
        self.time_limit_ms = int(testset.find('time-limit').text)
        self.memory_limit_kb = int(testset.find('memory-limit').text) // 1024
        self.test_count = int(testset.find('test-count').text)
        self.input_path_pattern = self.build_path(testset.find('input-path-pattern').text)
        self.output_path_pattern = self.build_path(testset.find('answer-path-pattern').text)

        checker_source = root.find('assets').find('checker').find('source')
        self.testlib_path = self.build_path(os.path.join('files', 'testlib.h'))
        self.checker_source_path = self.build_path(checker_source.attrib['path'])
        self.checker_binary_path = self.build_path('check.out')
        self.checker_language = self.match_language(checker_source.attrib['type'])

    def build_path(self, relpath):
        return os.path.join(self.package_path, relpath)

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
