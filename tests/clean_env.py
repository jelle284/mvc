import shutil
import os

def rmfiles(files_to_delete, subdir):
    for filename in files_to_delete:
        file_path = os.path.join(subdir, filename)
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

# remove backend files
shutil.rmtree("./mvc-files", ignore_errors=True)

# remove workspace 0
rmfiles(
    files_to_delete = [".mvc", "changelog.md", "f1.txt", "f2.txt"],
    subdir = "./tests/subws0"
)

# remove workspace 1
rmfiles(
    files_to_delete = [".mvc", "f1.txt", "f2.txt"],
    subdir = "./tests/subws1"
)

# remove helpers
rmfiles(
    files_to_delete = ["project.json", "version.json", "workspace.json"],
    subdir = "./tests"
)