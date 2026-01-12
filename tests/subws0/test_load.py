import sys
sys.path.append("./.")

import os

from mvc.core import MiniVC
base_path = os.path.join(".", "mvc-files")
user_path = os.path.dirname(__file__)
mvc = MiniVC(base_path, user_path)

mvc.load("test_prj", "ver1")
print("status:")
print(mvc.status())
print("list:")
print(mvc.list())
print("contents:")
print(mvc.contents())
mvc.review()