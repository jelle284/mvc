import shutil
import os

shutil.rmtree("./mvc-files", ignore_errors=True)

files_to_delete = [".mvc", "changelog.txt", "f1.txt", "f2.txt"]
subdir = "./test/subws0"

for filename in files_to_delete:
    file_path = os.path.join(subdir, filename)
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


files_to_delete = [".mvc"]
subdir = "./test/subws1"

for filename in files_to_delete:
    file_path = os.path.join(subdir, filename)
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass