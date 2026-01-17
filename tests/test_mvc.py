import unittest
from mvc.core import MiniVC, FileOperation
import os
import shutil

PRJ_NAME = "test_prj"
BASE_PATH = os.path.join(".", "mvc-files")

def confirmation_dialog(recipe: FileOperation):
    if len(recipe.files_to_add) > 0:
        print(f"    confirm adding files: {', '.join(file for file in recipe.files_to_add)}")
    if len(recipe.files_to_remove) > 0:
        print(f"    confirm removing files: {', '.join(file for file in recipe.files_to_remove)}")

def create_subws(name: str):
    user_path = os.path.join(os.path.dirname(__file__), name)
    os.makedirs(user_path, exist_ok=True)
    return user_path

def create_subws_with_files(name: str, i_start: int, i_end: int):
    user_path = create_subws(name)
    for i in range(i_start, i_end + 1):
        with open(os.path.join(user_path, f"f{i}.txt"), 'w') as fd:
            fd.write(f"test file {i}")
    return user_path

class TestMVC(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE_PATH, exist_ok=True)
        print("setup done")

    def tearDown(self):
        shutil.rmtree("./mvc-files", ignore_errors=True)
        for i in range(1,6):
            shutil.rmtree(f"tests/subws{i}", ignore_errors=True)
        print("teardown done")

    def test(self):
        def subtest_1():
            print("from subws1")
            user_path = create_subws_with_files("subws1", 1, 3)
            user_files = os.listdir(user_path)
            mvc = MiniVC(BASE_PATH, user_path)
            mvc.create(PRJ_NAME)
            project_path = os.path.join(BASE_PATH, PRJ_NAME)
            self.assertTrue(os.path.exists(project_path))
            print("  changes")
            self.assertListEqual(user_files, mvc.changes())
            print("  submit")
            mvc.submit(["f1.txt"], "first text file")
            self.assertIn("f1.txt", mvc.contents())
            print("  save")
            mvc.save("first content saved")
            print("  release")
            mvc.release("archive this milestone")
            print("  submit")
            mvc.submit(["f2.txt", "f3.txt"], "new content")
            print("  changes")
            self.assertEqual(len(mvc.changes()), 0)
            print("  Done!")

        def subtest_2():
            print("from subws2")
            user_path = create_subws("subws2")
            mvc = MiniVC(BASE_PATH, user_path)
            print("  list:")
            self.assertIn(PRJ_NAME, mvc.list_projects())
            print("  load")
            recipe = mvc.load(PRJ_NAME)
            self.assertIn("f1.txt", recipe.files_to_add)
            confirmation_dialog(recipe)
            mvc.load_finalize(recipe)
            self.assertIn("f1.txt", os.listdir(user_path))
            status = mvc.status()
            print("  status:", status)
            print("  review")
            recipe = mvc.review()
            expected_files = ("f1.txt", "f2.txt", "f3.txt")
            for f in expected_files:
                self.assertIn(f, recipe.files_to_add)
            confirmation_dialog(recipe)
            mvc.review_finalize(recipe)
            for f in expected_files:
                self.assertIn(f, os.listdir(user_path))
            print("  remove")
            mvc.remove(["f3.txt"], "i didn't like this part")
            self.assertNotIn("f3.txt", mvc.contents())
            self.assertNotIn("f3.txt", os.listdir(user_path))
            print("  save")
            mvc.save("reviewed ok")
            print("  Done!")
        
        def subtest_3():
            print("from subws3")
            user_path = create_subws_with_files("subws3", 4, 6)
            mvc = MiniVC(BASE_PATH, user_path)
            print("  load")
            recipe = mvc.load(PRJ_NAME)
            confirmation_dialog(recipe)
            mvc.load_finalize(recipe)
            self.assertTrue(all(f in os.listdir(user_path) for f in ["f1.txt", "f2.txt", "changelog.md", ".mvc"]))
            mvc.remove(["f2.txt", "f1.txt"], "its out")
            user_files = os.listdir(user_path)
            self.assertFalse(any(f in user_files for f in ["f2.txt", "f1.txt"]))
            mvc.submit(["f4.txt", "f5.txt", "f6.txt"], "lots text file")
            print("  Done!")

        def subtest_4():
            print("from subws4")
            user_path = create_subws("subws4")
            mvc = MiniVC(BASE_PATH, user_path)
            mvc.load_finalize(mvc.load(PRJ_NAME))
            status = mvc.status()
            print("  status:", status)
            mvc.review_finalize(mvc.review())
            user_files = os.listdir(user_path)
            self.assertTrue(all(f in user_files for f in ["f4.txt", "f5.txt", "f6.txt"]))
            mvc.save("ready for release")
            mvc.release("second generation")
            changes = mvc.changes()
            self.assertTrue(all(f in changes for f in ["f2.txt", "f1.txt"]))
            print("  Done!")

        def subtest_5():
            print("from subws5")
            user_path = create_subws("subws5")
            mvc = MiniVC(BASE_PATH, user_path)
            print("  load release 1")
            mvc.load_finalize(mvc.load(PRJ_NAME, 1))
            user_files = os.listdir(user_path)
            expected_files = ["f1.txt", ".mvc", "changelog.md"]
            self.assertTrue(all(f in user_files for f in expected_files))
            self.assertFalse(any(f not in user_files for f in expected_files))
            print("  Done!")

        subtest_1()
        subtest_2()
        subtest_3()
        subtest_4()
        subtest_5()

if __name__ == '__main__':
    unittest.main()
