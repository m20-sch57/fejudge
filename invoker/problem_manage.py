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

        checker = root.find('assets').find('checker')
        self.checker_type = checker.attrib.get('type') or ''
        self.checker_source_path = self.build_path(checker.find('source').attrib['path'])
        self.checker_binary_path = self.build_path('check.out')
        self.checker_language = self.match_language(checker.find('source').attrib['type'])

        self.executables = []
        if root.find('files').find('executables') is not None:
            for child in root.find('files').find('executables'):
                source = child.find('source')
                self.executables.append({
                    'path': self.build_path(source.attrib['path']),
                    'language': self.match_language(source.attrib['type'])
                })

        main_solution_source = root.find('assets').find('solutions').find('.//*[@tag="main"]').find('source')
        self.main_solution_source_path = self.build_path(main_solution_source.attrib['path'])
        self.main_solution_language = self.match_language(main_solution_source.attrib['type'])

        self.tests = []
        self.test_points_enabled = False
        for ind, test in enumerate(testset.find('tests')):
            test_number = ind + 1
            test_group = test.attrib.get('group') or ''
            test_points = float(test.attrib.get('points')) if test.attrib.get('points') else 0
            if test_points:
                self.test_points_enabled = True
            test_info = {
                'test_number': test_number,
                'group': test_group,
                'points': test_points,
                'generate_input': not os.path.exists(self.test_input_path(test_number)),
                'generate_output': not os.path.exists(self.test_output_path(test_number))
            }
            if test.attrib['method'] == 'generated':
                argv = test.attrib['cmd'].split()
                test_info['program'] = argv[0]
                test_info['additional_argv'] = argv[1:]
            self.tests.append(test_info)

        self.groups = dict()
        if testset.find('groups') is not None:
            for group in testset.find('groups'):
                name = group.attrib['name']
                group_points_policy = group.attrib.get('points-policy') or ''
                group_info = {
                    'points-policy': group_points_policy,
                    'dependencies': []
                }
                if group.find('dependencies') is not None:
                    for dependency in group.find('dependencies'):
                        group_info['dependencies'].append(dependency.attrib['group'])
                self.groups[name] = group_info
        else:
            default_points_policy = 'each-test' if self.test_points_enabled else 'complete-group'
            self.groups[''] = {
                'points-policy': default_points_policy,
                'dependencies': []
            }

        self.group_test_indices = dict([(name, []) for name in self.groups.keys()])
        for ind, test_info in enumerate(self.tests):
            test_group = test_info['group']
            self.group_test_indices[test_group].append(ind)

        self.group_order = self.generate_group_order()
        self.test_order = self.generate_test_order()

    def problem_name(self, language='english'):
        return self.select_language(self.names_dict, language)

    def html_dir(self, language='english'):
        return self.select_language(self.html_dir_dict, language)

    def pdf_dir(self, language='english'):
        return self.select_language(self.pdf_dir_dict, language)

    def build_path(self, relpath: str):
        return os.path.join(self.package_path, relpath)

    def test_input_path(self, test_number: int):
        return self.input_path_pattern % test_number

    def test_output_path(self, test_number: int):
        return self.output_path_pattern % test_number

    def generate_group_order(self):
        def dfs(u):
            visited.add(u)
            for v in self.groups[u]['dependencies']:
                if v not in visited:
                    dfs(v)
            order.append(u)

        order = []
        visited = set()
        for group in self.groups.keys():
            if group not in visited:
                dfs(group)
        return order

    def generate_test_order(self):
        test_order = []
        for group in self.group_order:
            for ind in self.group_test_indices[group]:
                test_order.append(ind)
        return test_order

    @staticmethod
    def select_language(dictionary: dict, language: str):
        return dictionary[language] if language in dictionary.keys() else next(iter(dictionary.values()))

    @staticmethod
    def match_language(language: str):
        if language.startswith('cpp'):
            return 'cpp'
        elif language.startswith('py'):
            return 'py'
