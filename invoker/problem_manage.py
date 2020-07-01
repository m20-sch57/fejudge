import os
import xml.etree.ElementTree as ET

from config import Config


class ProblemManager:
    def __init__(self, problem_id):
        self.problem_id = problem_id
        self.package_path = os.path.join(Config.PROBLEMS_PATH, str(self.problem_id))
        self.xml_path = self.build_path('problem.xml')

        tree = ET.parse(self.xml_path)
        root = tree.getroot()

        self.names_dict = dict()
        for child in root.find('names'):
            self.names_dict[child.attrib['language']] = child.attrib['value']

        self.html_dir_dict = dict()
        self.pdf_dir_dict = dict()
        for child in root.find('statements'):
            curdir = os.path.abspath(os.path.dirname(self.build_path(child.attrib['path'])))
            if child.attrib['type'] == 'text/html':
                self.html_dir_dict[child.attrib['language']] = curdir
            elif child.attrib['type'] == 'application/pdf':
                self.pdf_dir_dict[child.attrib['language']] = curdir

        testset = root.find('judging')[0]
        self.time_limit_ms = int(testset.find('time-limit').text)
        self.memory_limit_kb = int(testset.find('memory-limit').text) // 1024
        self.test_count = int(testset.find('test-count').text)
        self.input_path_pattern = self.build_path(testset.find('input-path-pattern').text)
        self.output_path_pattern = self.build_path(testset.find('answer-path-pattern').text)

        self.testlib_path = self.build_path(os.path.join('files', 'testlib.h'))

        checker_source = root.find('assets').find('checker').find('source')
        self.checker_source_path = self.build_path(checker_source.attrib['path'])
        self.checker_binary_path = self.build_path('check.out')
        self.checker_language = self.match_language(checker_source.attrib['type'])

        self.executables = []
        for child in root.find('files').find('executables'):
            source = child.find('source')
            self.executables.append({
                'path': self.build_path(source.attrib['path']),
                'language': self.match_language(source.attrib['type'])
            })

        main_solution_source = root.find('assets').find('solutions').find('.//*[@tag="main"]').find('source')
        self.main_solution_source_path = self.build_path(main_solution_source.attrib['path'])
        self.main_solution_language = self.match_language(main_solution_source.attrib['type'])

        self.tests_to_generate = []
        for ind, test in enumerate(testset.find('tests')):
            test_number = ind + 1
            test_info = {
                'test_number': test_number,
                'generate_input': not os.path.exists(self.test_input_path(test_number)),
                'generate_output': not os.path.exists(self.test_output_path(test_number))
            }
            if test.attrib['method'] == 'generated':
                argv = test.attrib['cmd'].split()
                test_info['program'] = argv[0]
                test_info['additional_argv'] = argv[1:]
            self.tests_to_generate.append(test_info)

    def problem_name(self, language='english'):
        return self.select_language(self.names_dict, language)

    def html_dir(self, language='english'):
        return self.select_language(self.html_dir_dict, language)

    def pdf_dir(self, language='english'):
        return self.select_language(self.pdf_dir_dict, language)

    def build_path(self, relpath):
        return os.path.join(self.package_path, relpath)

    def test_input_path(self, test_number):
        return self.input_path_pattern % test_number

    def test_output_path(self, test_number):
        return self.output_path_pattern % test_number

    @staticmethod
    def select_language(dictionary, language):
        return dictionary[language] if language in dictionary.keys() else next(iter(dictionary.values()))

    @staticmethod
    def match_language(language):
        if language.startswith('cpp'):
            return 'cpp'
        elif language.startswith('py'):
            return 'py'
