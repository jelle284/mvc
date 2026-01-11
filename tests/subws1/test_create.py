import sys
sys.path.append(".")

import os

from mvc.core import MiniVC

file_dir = os.path.dirname(__file__)

for file in ["f1.txt", "f2.txt"]:
    with open(os.path.join(file_dir, file), 'w') as fd:
        fd.write("mvc test file")

mvc = MiniVC("mvc-files", file_dir)
mvc.create("test_prj")
mvc.submit(["f1.txt"], "first")
mvc.save("saved")
mvc.release()
print("changes:")
print(mvc.changes())
mvc.submit(["f2.txt"], "second")
mvc.remove(["f2.txt"])
mvc.remove(["f1.txt"])
print("status:")
print(mvc.status())