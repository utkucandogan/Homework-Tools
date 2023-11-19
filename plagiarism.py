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

class Plagiarism:
    def __init__(self, config: dict, pwd: str = ""):
        try:
            self.pwd: str  = os.path.join(pwd, config.get("pwd", ""))
            self.test: str = os.path.join(self.pwd, config["test"])

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

        except KeyError as e:
            raise RuntimeError(f"Config file requires {e} in \"plagiarism\" entry.")

    # This function extracts a student's code into a folder for
    # copy detection. It flattens the file structure. (There was an
    # error in the copydetect tool that results in a self-plagiarism
    # if a student used the same code in multiple places under different
    # folders. I did not check if this error is fixed.)
    def extract_single(self, zfile: zip.ZipFile, extTo: str, prefix: str):
        os.makedirs(extTo, exist_ok=True)
        for file in zfile.namelist():
            if file.endswith(tuple(self.extensions)):
                flatFile = prefix + "%" + file.replace("/", "%").replace("\\", "%")
                targetPath = os.path.join(extTo, flatFile)
                with zfile.open(file) as source, open(targetPath, "wb") as target:
                    shutil.copyfileobj(source, target)
                try:
                    to_utf8(targetPath)
                except (UnicodeEncodeError, UnicodeDecodeError) as e:
                    print(f"Warning: {targetPath} couldn't be converted to UTF-8. Removing...")
                    os.remove(targetPath)

    # This function extracts each students' code into a folder for copy detection.
    def extract(self, submissions: str):
        os.makedirs(self.test, exist_ok=True)
        for folder in os.listdir(submissions):
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
                        self.extract_single(zf, extTo, file)
                except zip.BadZipFile:
                    print(f"Warning: {user} has invalid zip file!")

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
