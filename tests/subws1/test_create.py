import sys
sys.path.append(".")

import os

from mvc.core import MiniVC

user_path = os.path.dirname(__file__)

# create some files in our workspace
for file in ["f1.txt", "f2.txt"]:
    with open(os.path.join(user_path, file), 'w') as fd:
        fd.write("mvc test file")

# create the base path directory
base_path = os.path.join(".", "mvc-files")
os.makedirs(base_path, exist_ok=True)

# test seq
mvc = MiniVC(base_path, user_path)
mvc.create("test_prj")
mvc.submit(["f1.txt"], "first text file")
mvc.save("Initial version with one text file")
mvc.release()
print("changes:")
print(mvc.changes())
mvc.submit(["f2.txt"], "second text file")
mvc.remove(["f2.txt"])
mvc.remove(["f1.txt"])
print("status:")
print(mvc.status())