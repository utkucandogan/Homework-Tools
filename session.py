import os, shutil

class Session:
    def __init__(self, config: dict, pwd: str = ""):
        try:
            self.pwd: str      = os.path.join(pwd, config.get("pwd", ""))
            self.sessions: str = os.path.join(self.pwd, config["sessions"])

            self.session_list: list[list[str]] = config["session_list"]

            self.session_name_format: str = config.get("session_name_format", "Session-{no}")
            self.table_name_format: str   = config.get("table_name_format", "Table-{no}")
            self.use_folder_name: bool    = config.get("use_folder_name", False)

        except KeyError as e:
            raise RuntimeError(f"Config file requires {e} in \"session\" entry.")
        
    # This function finds the correct session for the student. In order to function correctly,
    # student's zip file must contain their id in the filename
    def find(self, filename: str) -> tuple[int, int] | None:
        for i, session in enumerate(self.session_list):
            for j, id in enumerate(session):
                if id in filename:
                    return (i+1,j+1)
        return None
    
    # This function groups submissions (or reports) into correct subfolders
    def group(self, path: str):
        for folder in os.listdir(path):
            user = os.path.join(path, folder)
            if not os.path.isdir(user):
                continue

            if self.use_folder_name:
                session = self.find(user)

            for file in os.listdir(user):
                if not self.use_folder_name:
                    session = self.find(file)

                print(f"Processing: {file}")
                filepath = os.path.join(user, file)
                new_path = ""
                if session is None:
                    new_path = os.path.join(self.sessions, "ERROR", folder)
                    os.makedirs(new_path, exist_ok=True)
                else:
                    session_name = self.session_name_format.format(no=session[0])
                    table_name = self.table_name_format.format(no=session[1])
                    new_path = os.path.join(self.sessions, session_name, table_name)
                shutil.copy2(filepath, new_path)

    # This function creates folders and groups all the submissions
    def create(self, submissions: list[str]):
        os.makedirs(self.sessions, exist_ok=True)
        for i, session in enumerate(self.session_list):
            session_name = self.session_name_format.format(no=i+1)
            session_path = os.path.join(self.sessions, session_name)
            os.makedirs(session_path, exist_ok=True)

            for j, _ in enumerate(session):
                table_name = self.table_name_format.format(no=j+1)
                table_path = os.path.join(session_path, table_name)
                os.makedirs(table_path, exist_ok=True)

        error_path = os.path.join(self.sessions, "ERROR")
        os.makedirs(error_path, exist_ok=True)

        for path in submissions:
            self.group(path)

if __name__ == "__main__":
    print("This is a library file. Run \"main.py\"!")
