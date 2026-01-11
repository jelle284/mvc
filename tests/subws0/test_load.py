import sys
sys.path.append("./.")

import os

from mvc.core import MiniVC

mvc = MiniVC("mvc-files", os.path.dirname(__file__))

mvc.load("test_prj", "ver1")
print("status:")
print(mvc.status())
print("list:")
print(mvc.list())
print("contents:")
print(mvc.contents())
mvc.review()