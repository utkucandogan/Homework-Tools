import os, shutil
import json
import zipfile as zip
from copydetect import CopyDetector

# Checks is path2 is empty. If not, joins path1 and path2
def path_or_none(path1: str, path2: str) -> str | None:
    if bool(path2):
        return os.path.join(path1, path2)
    else:
        return None

class HomeworkTools:
    def __init__(self, config_path: str):
        config = {}
        with open(config_path, "r") as f:
            config_data = f.read()
            config = json.loads(config_data)
        
        self.pwd: str                = config["pwd"]
        self.submissions: str        = os.path.join(config["pwd"], config["submissions"])
        self.reports: str | None     = path_or_none(config["pwd"], config["reports"])
        self.sessions: str           = os.path.join(config["pwd"], config["sessions"])
        self.plagiarism: str         = os.path.join(config["pwd"], config["plagiarism"])
        self.boilerplate: str | None = path_or_none(config["pwd"], config["boilerplate"])

        self.session_list: list[list[str]] = config["session_list"]

        self.plagiarism_extensions: list[str]    = config["plagiarism_extensions"]
        self.plagiarism_noise_threshold: int     = config["plagiarism_threshold"]
        self.plagiarism_guarantee_threshold: int = config["plagiarism_threshold"]
        self.plagiarism_display_threshold: float = config["plagiarism_percentage"]

        self.session_session_name_format: str = config["session_session_name_format"]
        self.session_table_name_format: str   = config["session_table_name_format"]

    # This function extracts a student's code into a folder for
    # copy detection. It flattens the file structure. (There was an
    # error in the copydetect tool that results in a self-plagiarism
    # if a student used the same code in multiple places under different
    # folders. I did not check if this error is fixed.)
    def plagiarism_extract_single(self, zfile: zip.ZipFile, extTo: str):
        os.makedirs(extTo, exist_ok=True)
        for file in zfile.namelist():
            if file.endswith(tuple(self.plagiarism_extensions)):
                flatFile = file.replace("/", "%").replace("\\", "%")
                targetPath = os.path.join(extTo, flatFile)
                with zfile.open(file) as source, open(targetPath, "wb") as target:
                    shutil.copyfileobj(source, target)

    # This function extracts each students' code into a folder for copy detection.
    def plagiarism_extract(self):
        os.makedirs(self.plagiarism, exist_ok=True)
        for folder in os.listdir(self.submissions):
            user = os.path.join(self.submissions, folder)
            if not os.path.isdir(user):
                continue

            print(f"Extracting: {user}")
            for file in os.listdir(user):
                zfile = os.path.join(user, file)
                if not zfile.endswith(".zip"):
                    continue

                try:
                    with zip.ZipFile(zfile) as zf:
                        extTo = os.path.join(self.plagiarism, folder)
                        self.plagiarism_extract_single(zf, extTo)
                except zip.BadZipFile:
                    print(f"Warning: {user} has invalid zip file!")

    # This function checks for plagiarism using copydetect library
    def plagiarism_check(self):
        detector = CopyDetector(test_dirs=self.plagiarism, boilerplate_dirs=self.boilerplate, extensions=self.plagiarism_extensions,
                                noise_t=self.plagiarism_noise_threshold, guarantee_t=self.plagiarism_guarantee_threshold,
                                display_t=self.plagiarism_display_threshold, ignore_leaf=True)
        detector.run()
        detector.generate_html_report()
    
    # This function finds the correct session for the student. In order to function correctly,
    # student's zip file must contain their id in the filename
    def session_find(self, filename: str) -> tuple[int, int] | None:
        for i, session in enumerate(self.session_list):
            for j, id in enumerate(session):
                if id in filename:
                    return (i+1,j+1)
        return None
    
    # This function groups submissions (or reports) into correct subfolders
    def session_group(self, path: str):
        for folder in os.listdir(path):
            user = os.path.join(path, folder)
            if not os.path.isdir(user):
                continue

            for file in os.listdir(user):
                print(f"Processing: {file}")
                filepath = os.path.join(user, file)
                session = self.session_find(file)
                new_path = ""
                if session is None:
                    new_path = os.path.join(self.sessions, "ERROR", folder)
                    os.makedirs(new_path, exist_ok=True)
                else:
                    session_name = self.session_session_name_format.format(no=session[0])
                    table_name = self.session_table_name_format.format(no=session[1])
                    new_path = os.path.join(self.sessions, session_name, table_name)
                shutil.copy2(filepath, new_path)

    # This function creates folders and groups all the submissions
    def session_create(self):
        os.makedirs(self.sessions, exist_ok=True)
        for i, session in enumerate(self.session_list):
            session_name = self.session_session_name_format.format(no=i+1)
            session_path = os.path.join(self.sessions, session_name)
            os.makedirs(session_path, exist_ok=True)

            for j, _ in enumerate(session):
                table_name = self.session_table_name_format.format(no=j+1)
                table_path = os.path.join(session_path, table_name)
                os.makedirs(table_path, exist_ok=True)

        error_path = os.path.join(self.sessions, "ERROR")
        os.makedirs(error_path, exist_ok=True)

        self.session_group(self.submissions)
        if self.reports is not None:
            self.session_group(self.reports)
