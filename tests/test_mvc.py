import unittest
from mvc.core import MiniVC, MVCError
from mvc.helpers import list_files_dir, FileID, Project, Version
import os
import shutil
from pathlib import Path

PRJ_NAME = "test_prj"
BASE_PATH = Path(".", "mvc-files")
USER_ROOT = Path(os.path.dirname(__file__))

def create_subws(name: str):
    user_path =  USER_ROOT / name
    user_path.mkdir(exist_ok=True)
    return user_path

def create_subws_with_files(name: str, i_start: int, i_end: int):
    user_path = create_subws(name)
    for i in range(i_start, i_end + 1):
        with open(user_path / f"f{i}.txt", 'w') as fd:
            fd.write(f"test file {i}")
    return user_path

class TestMVC(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE_PATH, exist_ok=True)
        print("setup done")

    def tearDown(self):
        shutil.rmtree("./mvc-files", ignore_errors=True)
        for i in range(1,7):
            shutil.rmtree(f"tests/subws{i}", ignore_errors=True)
        print("teardown done")

    def test_create(self):
        print("test create")
        user_path = create_subws_with_files("subws1", 1, 3)
        mvc = MiniVC(BASE_PATH, user_path, "user1")
        mvc.create(PRJ_NAME)
        project_path = Path(BASE_PATH) / PRJ_NAME
        self.assertTrue(project_path.exists())
        self.assertRaises(MVCError, mvc.create, PRJ_NAME)
    
    def test_submit(self):
        print("test submit")
        user_path = create_subws_with_files("subws1", 1, 3)
        mvc = MiniVC(BASE_PATH, user_path, "user1")
        mvc.create(PRJ_NAME)
        self.assertRaises(MVCError, mvc.submit, [])
        self.assertRaises(MVCError, mvc.submit, ["file_which_does_not_exist.txt"])
        mvc.submit(["f1.txt"])
        expected_path = BASE_PATH / PRJ_NAME / "temp" / "sub1"
        self.assertTrue(expected_path.exists())
        self.assertIn("f1.txt", list_files_dir(expected_path))
        mvc.submit(["f2.txt"])
        project = Project.load(BASE_PATH / PRJ_NAME)
        self.assertEqual(project.id.dev, 2)
        version = Version.load(BASE_PATH / PRJ_NAME / project.id.sub_path)
        self.assertIn("f1.txt", version.include)
        self.assertEqual(FileID(0,0,1), version.include["f1.txt"])

    def test_remove(self):
        print("test remove")
        user_path = create_subws_with_files("subws1", 1, 3)
        mvc = MiniVC(BASE_PATH, user_path, "user1")
        mvc.create(PRJ_NAME)
        self.assertRaises(MVCError, mvc.remove, [])
        self.assertRaises(MVCError, mvc.remove, ["file_which_does_not_exist.txt"])
        mvc.submit(["f1.txt", "f2.txt", "f3.txt"])
        mvc.remove(["f2.txt"])
        project = Project.load(BASE_PATH / PRJ_NAME)
        self.assertEqual(project.id.dev, 2)
        version = Version.load(BASE_PATH / PRJ_NAME / project.id.sub_path)
        self.assertNotIn("f2.txt", version.include)

    def test_accept(self):
        print("test accept")
        user_path = create_subws_with_files("subws1", 1, 3)
        mvc = MiniVC(BASE_PATH, user_path, "user1")
        mvc.create(PRJ_NAME)
        self.assertRaises(MVCError, mvc.accept)
        mvc.submit(["f1.txt", "f2.txt", "f3.txt"])
        mvc.accept()
        expected_path = BASE_PATH / PRJ_NAME / "versions" / "latest"
        self.assertTrue(expected_path.exists())
        expected_files = ["f1.txt", "f2.txt", "f3.txt"]
        version_files = list_files_dir(expected_path)
        self.assertTrue(all(f in version_files for f in expected_files))

    def test_changes(self):
        print("test changes")
        user_path = create_subws_with_files("subws1", 1, 3)
        mvc = MiniVC(BASE_PATH, user_path, "user1")

        mvc.create(PRJ_NAME)
        user_files = list_files_dir(user_path)
        new_files, changed_files = mvc.changes()
        self.assertListEqual(user_files, new_files)
        mvc.submit(["f1.txt", "f2.txt"])
        new_files, changed_files = mvc.changes()
        self.assertListEqual(["f3.txt"], new_files)
        with open(Path("tests", "subws1", "f1.txt"), 'w') as fd:
            fd.write("altered content")
        new_files, changed_files = mvc.changes()
        self.assertIn("f1.txt", changed_files)
        mvc.submit(["f1.txt"])
        new_files, changed_files = mvc.changes(FileID(0,0,1))
        self.assertIn("f1.txt", changed_files)
    
    def test_claims(self):
        print("test claims")
        def subtest_1():
            user_path = create_subws_with_files("subws1", 1, 3)
            user_files = list_files_dir(user_path)
            mvc = MiniVC(BASE_PATH, user_path, "user1")
            mvc.create(PRJ_NAME)
            self.assertRaises(MVCError, mvc.claim, user_files[:1])
            mvc.submit(user_files)
            mvc.claim(user_files[:1])

        def subtest_2():
            user_path = create_subws("subws2")
            mvc = MiniVC(BASE_PATH, user_path, "user2")
            mvc.load(PRJ_NAME)
            mvc.collect(mvc.available()[0])
            user_files = list_files_dir(user_path)
            self.assertRaises(MVCError, mvc.submit, user_files)
            mvc.unclaim(user_files[:1], force=True)
            mvc.submit(user_files)

        subtest_1()
        subtest_2()

    def test_collect(self):
        print("test collect")
        def subtest_1():
            user_path = create_subws_with_files("subws1", 1, 3)
            mvc = MiniVC(BASE_PATH, user_path, "user1")
            mvc.create(PRJ_NAME)
            mvc.submit(["f1.txt"], "the first file")
            mvc.accept("first content accepted")
            mvc.release("first release")
            mvc.submit(["f2.txt"], "the second file")
            mvc.accept("second content accepted")
            mvc.submit(["f3.txt"], "the third file")
            with open(Path("tests", "subws1", "f1.txt"), 'w') as fd:
                fd.write("altered content")
            mvc.submit(["f1.txt"], "changed the first file")
            available = mvc.available()
            self.assertEqual(available[0], FileID(1,1,2))
            self.assertEqual(available[1], FileID(1,1,1))
            self.assertEqual(available[2], FileID(1,1,0))
            self.assertEqual(available[3], FileID(1,0,0))

        def subtest_2():
            user_path = create_subws("subws2")
            mvc = MiniVC(BASE_PATH, user_path, "user2")
            mvc.load(PRJ_NAME)
            mvc.collect(mvc.available()[0])
            user_files = list_files_dir(user_path)
            expected_files = ["f1.txt", "f2.txt", "f3.txt"]
            self.assertTrue(all(f in user_files for f in expected_files))
            self.assertFalse(any(f not in user_files for f in expected_files))
            with open(str(Path("tests", "subws2", "f1.txt")), 'r') as fd:
                f1_content = fd.read()
                self.assertEqual(f1_content, "altered content")
            
        def subtest_3():
            user_path = create_subws("subws2")
            mvc = MiniVC(BASE_PATH, user_path, "user2")
            mvc.load(PRJ_NAME)
            mvc.collect(mvc.available()[1])
            user_files = list_files_dir(user_path)
            expected_files = ["f1.txt", "f2.txt", "f3.txt"]
            self.assertTrue(all(f in user_files for f in expected_files))
            self.assertFalse(any(f not in user_files for f in expected_files))
            with open(str(Path("tests", "subws2", "f1.txt")), 'r') as fd:
                f1_content = fd.read()
                self.assertEqual(f1_content, "test file 1")

        def subtest_4():
            user_path = create_subws("subws4")
            mvc = MiniVC(BASE_PATH, user_path, "user4")
            mvc.load(PRJ_NAME)
            mvc.collect(mvc.available()[2])
            user_files = list_files_dir(user_path)
            expected_files = ["f1.txt", "f2.txt"]
            self.assertTrue(all(f in user_files for f in expected_files))
            self.assertFalse(any(f not in user_files for f in expected_files))

        def subtest_5():
            user_path = create_subws("subws5")
            mvc = MiniVC(BASE_PATH, user_path, "user5")
            mvc.load(PRJ_NAME)
            mvc.collect(mvc.available()[3])
            user_files = list_files_dir(user_path)
            expected_files = ["f1.txt"]
            self.assertTrue(all(f in user_files for f in expected_files))
            self.assertFalse(any(f not in user_files for f in expected_files))

        subtest_1()
        subtest_2()
        subtest_3()
        subtest_4()
        subtest_5()

if __name__ == '__main__':
    unittest.main()
