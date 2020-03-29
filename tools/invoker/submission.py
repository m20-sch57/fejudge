import os
import constants
from config import Config


class SubmissionManager:
    def __init__(self, submission):
        self.submission = submission
        self.problem = submission.problem
        self.submission_log_file = os.path.join(
            Config.SUBMISSIONS_LOG_PATH, str(self.submission.id).zfill(6) + '.txt')
        self.participant_source = os.path.join(
            Config.SUBMISSION_DIR, 'participant.' + submission.language)
        self.participant_binary = os.path.join(Config.SUBMISSION_DIR, 'participant.out')
        self.checker_binary = os.path.join(Config.SUBMISSION_DIR, 'checker.out')
        self.input_file = os.path.join(Config.SUBMISSION_DIR, 'input.txt')
        self.output_file = os.path.join(Config.SUBMISSION_DIR, 'output.txt')
        self.error_file = os.path.join(Config.SUBMISSION_DIR, 'error.txt')
        self.answer_file = os.path.join(Config.SUBMISSION_DIR, 'answer.txt')
        self.result_file = os.path.join(Config.SUBMISSION_DIR, 'result.txt')
        self.compile_argv = constants.COMPILE_ARGV[self.submission.language]
        self.run_argv = constants.RUN_ARGV[self.submission.language]
        self.checker_argv = ['./checker.out', 'input.txt', 'output.txt', 'answer.txt', 'result.txt']

    def write_logs(self, message):
        fout = open(self.submission_log_file, 'a')
        fout.write(message)
        fout.close()

    @staticmethod
    def clear_data(items_to_stay=[]):
        for item in os.listdir(Config.SUBMISSION_DIR):
            if item not in items_to_stay:
                os.remove(os.path.join(Config.SUBMISSION_DIR, item))
