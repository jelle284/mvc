import sys
sys.path.append(".")

import os

from mvc.core import MiniVC
from tests import clean_env
clean_env.main()

user_path = os.path.dirname(__file__)

# create some files in our workspace
for i in range(10):
    with open(os.path.join(user_path, f"f{i}.txt"), 'w') as fd:
        fd.write("mvc test file")

# create the base path directory
base_path = os.path.join(".", "mvc-files")
os.makedirs(base_path, exist_ok=True)

# test seq
mvc = MiniVC(base_path, user_path)
mvc.create("test_prj")
mvc.submit(["f1.txt"], "first text file")
mvc.save()
mvc.release()
print("changes:")
print(mvc.changes())
mvc.submit(["f2.txt"], "second text file")
mvc.submit(["f3.txt"], "new content")
mvc.review()
mvc.save()
mvc.remove(["f2.txt", "f1.txt"], "its out")
mvc.save()
mvc.submit(["f4.txt", "f5.txt", "f6.txt"], "lots text file")
print("status:")
print(mvc.status())