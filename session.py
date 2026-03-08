import os, shutil
import csv
from pathlib import Path
import unicodedata

CSV_FILE = Path("students.csv")   # your CSV file with headers


def normalize(s: str) -> str:
    """Normalize Unicode for reliable name matching (Turkish-safe)."""
    s = unicodedata.normalize("NFKC", s)
    return s.strip().upper()


def load_id_map(csv_file):
    """
    Loads CSV of the form:
    "First name","Last name","ID number",...
    Returns dict: FULL NAME → ID
    """
    name_to_id = {}

    with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            first = row["First name"]
            last = row["Last name"]
            sid = row["ID number"]

            if not first or not last or not sid:
                continue

            full_name = normalize(f"{first} {last}")
            name_to_id[full_name] = sid

    return name_to_id


def extract_name_from_folder(folder_name: str) -> str:
    """
    From 'ERKAN ARKADAŞ_2574440_assignsubmission_file'
    extract 'ERKAN ARKADAŞ'
    """
    return folder_name.split("_")[0]

class Session:
    def __init__(self, config: dict, pwd: str = "",single_file: bool = False):
        try:
            self.pwd: str      = os.path.join(pwd, config.get("pwd", ""))
            self.sessions: str = os.path.join(self.pwd, config["sessions"])
            self.single_file: bool = single_file

            self.session_name_format: str = config.get("session_name_format", "Session-{no}")
            self.table_name_format: str   = config.get("table_name_format", "Table-{no}")

            if isinstance(config["session_list"], dict):
                self.session_list: dict[str, list[str]] = config["session_list"]
            else:
                self.session_list: dict[str, list[str]] = { self.session_name_format.format(no=i+1): v for i, v in enumerate(config["session_list"]) }

            self.id_map = load_id_map(CSV_FILE) if CSV_FILE.exists() else {}

        except KeyError as e:
            raise RuntimeError(f"Config file requires {e} in \"session\" entry.")
        
    # This function finds the correct session for the student. In order to function correctly,
    # student's zip file must contain their id in the filename
    def find(self, filename: str) -> tuple[str, int, str] | tuple[None, None, None]:
        basename = os.path.basename(filename)
        extracted_name = extract_name_from_folder(basename)
        student_id = self.id_map.get(normalize(extracted_name))
        
        search_target = student_id if student_id else filename

        for session_name, session in self.session_list.items():
            for i, id in enumerate(session):
                if id in search_target:
                    return session_name, i+1, id
        return None, None, None
    
    # This function groups submissions (or reports) into correct subfolders
    def group(self, path: str):
        for folder in os.listdir(path):
            if(self.single_file):
                file = folder
                user_file = os.path.join(path, file)
                
                if user_file:
                    session_name, table_no, id = self.find(user_file)

                print(f"Processing: {user_file}")
                filepath = user_file
                new_path = ""
                if id is None:
                    new_path = os.path.join(self.sessions, "ERROR", folder)
                    os.makedirs(new_path, exist_ok=True)
                else:
                    table_name = self.table_name_format.format(no=table_no, id=id)
                    new_path = os.path.join(self.sessions, session_name, table_name)
                shutil.copy2(filepath, new_path)
            else:
                user = os.path.join(path, folder)
                if not os.path.isdir(user):
                    continue
                #we use the folder's name for search
                session_name, table_no, id = self.find(user)

                #go over each file in the folder to extract
                for file in os.listdir(user):

                    print(f"Processing: {file}")
                    filepath = os.path.join(user, file)
                    new_path = ""
                    if id is None:
                        new_path = os.path.join(self.sessions, "ERROR", folder)
                        os.makedirs(new_path, exist_ok=True)
                    else:
                        table_name = self.table_name_format.format(no=table_no, id=id)
                        new_path = os.path.join(self.sessions, session_name, table_name)
                    shutil.copy2(filepath, new_path)    

    # This function creates folders and groups all the submissions
    def create(self, submissions: list[str]):
        os.makedirs(self.sessions, exist_ok=True)
        for session_name, session in self.session_list.items():
            session_path = os.path.join(self.sessions, session_name)
            os.makedirs(session_path, exist_ok=True)

            for i, id in enumerate(session):
                table_name = self.table_name_format.format(no=i+1, id=id)
                table_path = os.path.join(session_path, table_name)
                os.makedirs(table_path, exist_ok=True)

        error_path = os.path.join(self.sessions, "ERROR")
        os.makedirs(error_path, exist_ok=True)

        for path in submissions:
            self.group(path)

if __name__ == "__main__":
    print("This is a library file. Run \"main.py\"!")
