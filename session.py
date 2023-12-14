import os, shutil

class Session:
    def __init__(self, config: dict, pwd: str = "",single_file: bool = False):
        try:
            self.pwd: str      = os.path.join(pwd, config.get("pwd", ""))
            self.sessions: str = os.path.join(self.pwd, config["sessions"])
            self.single_file: bool = single_file

            self.session_name_format: str = config.get("session_name_format", "Session-{no}")
            self.table_name_format: str   = config.get("table_name_format", "Table-{no}")
            self.use_folder_name: bool    = config.get("use_folder_name", False)

            if isinstance(config["session_list"], dict):
                self.session_list: dict[str, list[str]] = config["session_list"]
            else:
                self.session_list: dict[str, list[str]] = { self.session_name_format.format(no=i+1): v for i, v in enumerate(config["session_list"]) }

        except KeyError as e:
            raise RuntimeError(f"Config file requires {e} in \"session\" entry.")
        
    # This function finds the correct session for the student. In order to function correctly,
    # student's zip file must contain their id in the filename
    def find(self, filename: str) -> tuple[str, int, str] | tuple[None, None, None]:
        for session_name, session in self.session_list.items():
            for i, id in enumerate(session):
                if id in filename:
                    return session_name, i+1, id
        return None, None, None
    
    # This function groups submissions (or reports) into correct subfolders
    def group(self, path: str):
        for folder in os.listdir(path):
            if(self.single_file):
                file = folder
                user_file = os.path.join(path, file)
                
                if self.user_file:
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

                if self.use_folder_name:
                    session_name, table_no, id = self.find(user)

                for file in os.listdir(user):
                    if not self.use_folder_name:
                        session_name, table_no, id = self.find(file)

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
