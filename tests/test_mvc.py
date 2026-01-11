import unittest
import shutil
import os
from mvc.core import MiniVC

class TestAsProducer(unittest.TestCase):
    def setUp(self):
        for file in ["f1.txt", "f2.txt"]:
            with open(file, 'w') as fd:
                fd.write("mvc test file")

    def tearDown(self):
        shutil.rmtree("mvc-files", ignore_errors=True)
        for filename in [".mvc", "changelog.txt", "f1.txt", "f2.txt"]:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

    def test(self):
        mvc = MiniVC("mvc-files", "")
        mvc.create("jesper")
        mvc.submit(["f1.txt"], "first")
        mvc.save("saved")
        mvc.release()
        mvc.submit(["f2.txt"], "second")
        status = mvc.status()

class TestAsConsumer(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test(self):
        pass


if __name__ == '__main__':
    unittest.main()