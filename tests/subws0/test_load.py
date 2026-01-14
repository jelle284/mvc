import sys
sys.path.append("./.")

import os

from mvc.core import MiniVC
base_path = os.path.join(".", "mvc-files")
user_path = os.path.dirname(__file__)
mvc = MiniVC(base_path, user_path)

print("list:")
print(mvc.list_projects())
mvc.load("test_prj", "ver1")
print("status:")
print(mvc.status())
print("contents:")
print(mvc.contents())