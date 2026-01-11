import sys
sys.path.append(".")

import os
import datetime
from mvc.helpers import MVCProject, MVCVersion, MVCWorkspace

workspace = MVCWorkspace("test_prj")
version = MVCVersion("sub3", datetime.datetime.now().isoformat(), "test version", {"file1.txt": "sub2"})
project = MVCProject("mvc-test", 0, 0, {})


workspace.save("tests/workspace.json")
version.save("tests/version.json")
project.save("tests/project.json")
