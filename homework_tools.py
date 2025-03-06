import os

from plagiarism import Plagiarism
from session import Session
from testbench import TestBench
class HomeworkTools:
    def __init__(self, config: dict):
        try:
            self.pwd: str      = config.get("pwd", "")
            self.submissions: str = os.path.join(self.pwd, config["submissions"])
            
            if "file_filter" in config:
                self.file_filter = config["file_filter"]
            if "single_file" in config:
                self.single_file = config["single_file"]
            else:
                self.single_file = False    
            if "reports" in config:
                self.reports = os.path.join(self.pwd, config["reports"])
            else:
                self.reports = None

            if "plagiarism" in config:
                self.plagiarism = Plagiarism(config["plagiarism"], self.pwd, self.single_file,self.file_filter)
            else:
                self.plagiarism = None

            if "testbench" in config:
                self.testbench = TestBench(config["testbench"], self.pwd, self.single_file,self.file_filter)
            else:
                self.plagiarism = None

            if "session" in config:
                self.session = Session(config["session"], self.pwd, self.single_file)
            else:
                self.session = None
            
        except KeyError as e:
            raise RuntimeError(f"Config file requires {e}.")

    # This function extracts each students' code into a folder for copy detection.
    def plagiarism_extract(self):
        if self.plagiarism is None:
            raise RuntimeError("HomeworkTools didn't configured for plagiarism.")
        self.plagiarism.extract(self.submissions)

        # This function extracts each students' code into a folder for autoamted cocotb tests.
    def testbench_extract(self):
        if self.testbench is None:
            raise RuntimeError("HomeworkTools didn't configured for testbench.")
        self.testbench.extract(self.submissions)

    # This function checks for plagiarism using copydetect library
    def plagiarism_check(self):
        if self.plagiarism is None:
            raise RuntimeError("HomeworkTools didn't configured for plagiarism.")
        self.plagiarism.check()

    # This function creates folders and groups all the submissions
    def session_create(self):
        if self.session is None:
            raise RuntimeError("HomeworkTools didn't configured for sessions.")
        paths = [self.submissions]
        if self.reports is not None:
            paths.append(self.reports)
        self.session.create(paths)

if __name__ == "__main__":
    print("This is a library file. Run \"main.py\"!")
