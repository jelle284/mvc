import sys
sys.path.append(".")

import os

from mvc.core import MiniVC

mvc = MiniVC("mvc-files", os.path.dirname(__file__))
mvc.create("jesper")
mvc.submit(["f1.txt"], "first")
mvc.save("saved")
mvc.release()
mvc.submit(["f2.txt"], "second")
print(mvc.status())