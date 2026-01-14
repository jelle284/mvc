import shutil
import os

def rmfiles(files_to_delete, subdir):
    for filename in files_to_delete:
        file_path = os.path.join(subdir, filename)
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

def main():
    # remove backend files
    shutil.rmtree("./mvc-files", ignore_errors=True)

    workspace_files = [".mvc", "changelog.md"] + [f"f{i}.txt" for i in range(10)]
    # remove workspace 0
    rmfiles(
        files_to_delete = workspace_files,
        subdir = "./tests/subws0"
    )

    # remove workspace 1
    rmfiles(
        files_to_delete = workspace_files,
        subdir = "./tests/subws1"
    )

    # remove helpers
    rmfiles(
        files_to_delete = ["project.json", "version.json", "workspace.json"],
        subdir = "./tests"
    )

if __name__ == '__main__':
    main()