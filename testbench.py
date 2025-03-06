import os, shutil
import zipfile as zip

# This function converts extracted files into utf8
def to_utf8(filepath: str):
    content = ""
    with open(filepath, "r") as f:
        content = f.read()
    content = content.encode("utf-8")
    with open(filepath, "wb") as f:
        f.write(content)

class TestBench:
    def __init__(self, config: dict, pwd: str = "", single_file: bool = False, file_filter: list = []):
        try:
            self.pwd: str  = os.path.join(pwd, config.get("pwd", ""))
            self.test: str = os.path.join(self.pwd, config["test"])
            self.single_file: bool = single_file
            self.file_filter: list = file_filter
            
            self.extensions: list[str] = config["extensions"]
        except KeyError as e:
            raise RuntimeError(f"Config file requires {e} in \"testbench\" entry.")

    # This function extracts a student's code into a folder.
    def extract_single(self, zfile: zip.ZipFile, extTo: str):
        os.makedirs(extTo, exist_ok=True)
        for file in zfile.namelist():
            if file.endswith(tuple(self.extensions)):
                file_name = os.path.basename(file)  # Preserve original file name
                if self.file_filter and os.path.splitext(file_name)[0] not in self.file_filter:
                    continue
                
                targetPath = os.path.join(extTo, file_name)
                with zfile.open(file) as source, open(targetPath, "wb") as target:
                    shutil.copyfileobj(source, target)
                
                try:
                    to_utf8(targetPath)
                except (UnicodeEncodeError, UnicodeDecodeError):
                    print(f"Warning: {targetPath} couldn't be converted to UTF-8. Removing...")
                    os.remove(targetPath)

    def extract(self, submissions: str):
        os.makedirs(self.test, exist_ok=True)
        for folder in os.listdir(submissions):
            if self.single_file:
                zfile = os.path.join(submissions, folder)
                if not zfile.endswith(".zip"):
                    continue
                print(f"Extracting: {zfile}")
                try:
                    with zip.ZipFile(zfile) as zf:
                        folder_name = os.path.splitext(folder)[0]  # Use the zip file name as folder name
                        extTo = os.path.join(self.test, folder_name)
                        self.extract_single(zf, extTo)
                except zip.BadZipFile:
                    print(f"Warning: {folder} has invalid zip file!")
            else:
                user = os.path.join(submissions, folder)
                if not os.path.isdir(user):        
                    continue
                print(f"Extracting: {user}")
                for file in os.listdir(user):
                    zfile = os.path.join(user, file)
                    if not zfile.endswith(".zip"):
                        continue
                    try:
                        with zip.ZipFile(zfile) as zf:
                            folder_name = os.path.splitext(file)[0]  # Use the zip file name as folder name
                            extTo = os.path.join(self.test, folder_name)
                            self.extract_single(zf, extTo)
                    except zip.BadZipFile:
                        print(f"Warning: {user} has invalid zip file!")

if __name__ == "__main__":
    print("This is a library file. Run \"main.py\"!")