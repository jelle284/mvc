import sys
sys.path.append("./.")

import os

from mvc.core import MiniVC

mvc = MiniVC("mvc-files", os.path.dirname(__file__))
print(mvc.list())
mvc.load("jesper", "ver1")
print(mvc.status())
mvc.review()