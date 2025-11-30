import os, shutil
import zipfile as zip

from common import to_utf8

class Plagiarism:
    def __init__(self, config: dict, pwd: str = "", zip_file: bool = True, single_file: bool = False, file_filter: list = []):
        try:
            self.pwd: str  = os.path.join(pwd, config.get("pwd", ""))
            self.test: str = os.path.join(self.pwd, config["test"])
            self.zip_file: bool = zip_file
            self.single_file: bool = single_file
            self.file_filter: list = file_filter

            self.reference: list[str] = [self.test]
            if "reference" in config:
                path = os.path.join(self.pwd, config["reference"])
                self.reference.append(path)

            self.boilerplate: list[str] = []
            if "boilerplate" in config:
                path = os.path.join(self.pwd, config["boilerplate"])
                self.boilerplate.append(path)

            self.extensions: list[str]    = config["extensions"]
            self.noise_threshold: int     = config["threshold"]
            self.guarantee_threshold: int = config["threshold"]
            self.display_threshold: float = config["percentage"]
            self.prefix: bool = config["prefix"]

        except KeyError as e:
            raise RuntimeError(f"Config file requires {e} in \"plagiarism\" entry.")
        
    def extract(self, submissions: str):
        if self.zip_file:
            self.zip_extract(submissions)
        else:
            self.folder_extract(submissions)

    # This function extracts a student's code into a folder for
    # copy detection. It flattens the file structure. (There was an
    # error in the copydetect tool that results in a self-plagiarism
    # if a student used the same code in multiple places under different
    # folders. I did not check if this error is fixed.)
    def zip_extract_single(self, zfile: zip.ZipFile, extTo: str, prefix: str):
        os.makedirs(extTo, exist_ok=True)
        for file in zfile.namelist():
            if file.endswith(tuple(self.extensions)):
                if self.file_filter:
                    #To only look at the file name and not the path
                    file_name = os.path.basename(file)
                    if not any(filter.casefold() in file_name.casefold() for filter in self.file_filter):
                        continue
                if(self.prefix):
                    flatFile = prefix + "%" + file.replace("/", "%").replace("\\", "%")
                else:
                    flatFile =os.path.basename(file)   
                targetPath = os.path.join(extTo, flatFile)
                with zfile.open(file) as source, open(targetPath, "wb") as target:
                    shutil.copyfileobj(source, target)
                try:
                    to_utf8(targetPath)
                except UnicodeError as e:
                    print(f"Warning: {targetPath} couldn't be converted to UTF-8. Error: {e} \n Removing...")
                    os.remove(targetPath)

    # This function extracts each students' code into a folder for copy detection.
    def zip_extract(self, submissions: str):
        os.makedirs(self.test, exist_ok=True)
        for folder in os.listdir(submissions):
            if self.single_file:
                zfile = os.path.join(submissions, folder)
                print(f"Extracting: {zfile}")
                if not zfile.endswith(".zip"):
                    continue
                try:
                    with zip.ZipFile(zfile) as zf:
                        extTo = os.path.join(self.test, folder)
                        self.zip_extract_single(zf, extTo, folder)
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
                            extTo = os.path.join(self.test, folder)
                            self.zip_extract_single(zf, extTo, file)
                    except zip.BadZipFile:
                        print(f"Warning: {user} has invalid zip file!")

    # Github classroom, does not use zip files, we need to iterate folder structure
    def folder_extract_single(self, student_folder: zip.ZipFile, extTo: str):
        os.makedirs(extTo, exist_ok=True)
        for root, dirs, files in os.walk(student_folder):
            rel_root = os.path.relpath(root, student_folder)
            if rel_root == ".":
                rel_root = ""

            for name in files:
                if not name.endswith(tuple(self.extensions)):
                    continue

                if self.file_filter:
                    if not any(filter.casefold() in name.casefold() for filter in self.file_filter):
                        continue

                source = os.path.join(root, name)
                flatFile = os.path.join(rel_root, name).replace("/", "%").replace("\\", "%")
                target = os.path.join(extTo, flatFile)
                shutil.copyfile(source, target)

    def folder_extract(self, submissions: str):
        os.makedirs(self.test, exist_ok=True)
        for folder in os.listdir(submissions):
            student_folder = os.path.join(submissions, folder)
            extTo = os.path.join(self.test, folder)

            print(f"Extracting: {folder}")
            self.folder_extract_single(student_folder, extTo)

    # This function checks for plagiarism using copydetect library
    def check(self):
        try:
            from copydetect import CopyDetector # unless used, it is not required
        except ModuleNotFoundError as e:
            print(f"For plagiarism check \"{e.name}\" module is required!")
            print("You can install it by running:")
            print(f"\tpip install {e.name}")
            exit(1)

        detector = CopyDetector(test_dirs=[self.test], ref_dirs=self.reference, boilerplate_dirs=self.boilerplate, extensions=self.extensions,
                                noise_t=self.noise_threshold, guarantee_t=self.guarantee_threshold, display_t=self.display_threshold,
                                ignore_leaf=True)
        detector.run()
        detector.generate_html_report()

if __name__ == "__main__":
    print("This is a library file. Run \"main.py\"!")
