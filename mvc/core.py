import os
import shutil
from typing import List
from datetime import datetime

from mvc.helpers import MVCError, Version, Project, Workspace, FileOperation, FileID, get_submit_path, get_stable_path, get_release_path, list_files_dir

class MiniVC:
    def _execute(self, recipe: FileOperation):
        for file, path in recipe.files_to_add.items():
            file_path = os.path.join(path, file)
            shutil.copy2(file_path, self.user_path)
        for file in recipe.files_to_remove:
            file_path = os.path.join(self.user_path, file)
            os.remove(file_path)
    
    def _get_history_markdown(self, project: Project) -> list[str]:
        md = []
        project_path = os.path.join(self.base_path, project.name)
        if project.id.submit > 0:
            md.append(f"# development version")
        for i in range(project.id.submit, 0, -1):
            version_path = os.path.join(project_path, get_submit_path(i))
            version = Version.load(version_path)
            for line in version.description:
                md.append(line)
        
        if project.id.save > 0:
            md.append(f"# stable version")
        version_path = os.path.join(project_path, get_stable_path())
        version = Version.load(version_path)
        for line in version.description:
            md.append(line)
        
        if project.id.release > 0:
            md.append(f"# Release version")
        for i in range(project.id.release, 0, -1):
            version_path = os.path.join(project_path, get_release_path(i))
            version = Version.load(version_path)
            for line in version.description:
                md.append(line)
        return md
    
    def _write_markdown(self, dst_path: str, md: List[str]):
        filename = os.path.join(dst_path, "changelog.md")
        with open(filename, 'w') as fd:
            for line in md:
                fd.write(line + "\n")

    def _current_timestamp(self) -> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _get_project(self, project_name):
        try:
            project_path = os.path.join(self.base_path, project_name)
            project = Project.load(project_path)
            return project, project_path
        except FileNotFoundError:
            raise MVCError("Invalid project name.")     
    
    def _get_workspace(self):
        try:
            workspace = Workspace.load(self.user_path)
            return workspace
        except FileNotFoundError:
            return None

    def __init__(self, base_path, user_path):
        self.base_path = base_path
        self.user_path = user_path
        if not os.path.exists(base_path):
            raise MVCError("Invalid base path.")

    def create(self, name: str):
        if name == '': raise MVCError("Project must have a name.")
        id = FileID(0,0,0)
        project = Project(
            name,
            id,
            {})
        project_path = os.path.join(self.base_path, name)
        try:
            os.makedirs(project_path)
        except OSError:
            raise MVCError("Trying to create project which already exists.")
        project.save(project_path)
        version = Version(
            [f"## {id}",
             f"{name} was created",
             self._current_timestamp()],
            {})
        version_path = os.path.join(project_path, id.sub_path)
        os.makedirs(version_path, exist_ok=True)
        version.save(version_path)
        workspace = Workspace(
            name,)
        workspace.save(self.user_path)

    def submit(self, files: List[str], comment: str = ""):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        version_path = os.path.join(project_path, project.id.sub_path)
        version = Version.load(version_path)
        work_files: list[str] = os.listdir(version_path)
        work_files.remove('.mvc')
        for file in work_files:
            version.include[file] = FileID.copy(project.id)
        for file in files:
            version.include.pop(file, None)
        project.id.submit += 1
        version_path = os.path.join(project_path, project.id.sub_path)
        os.makedirs(version_path, exist_ok=True)
        for file_name in files:
            src_path = os.path.join(self.user_path, file_name)
            dst_path = os.path.join(version_path, file_name)
            shutil.copy2(src_path, dst_path)
            project.timestamps[file_name] = os.path.getmtime(src_path)
        version.description = [f"## {project.id}",
                               comment,
                               f"### Submitted files:",
                               *[f' + {file}' for file in files],]
        workspace.save(self.user_path)
        version.save(version_path)
        project.save(project_path)

    def remove(self, files: List[str], comment: str = ""):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        version_path = os.path.join(project_path, project.id.sub_path)
        version = Version.load(version_path)
        work_files = os.listdir(version_path)
        work_files.remove('.mvc')
        for file in work_files:
            version.include[file] = FileID.copy(project.id)
        for file in files:
            version.include.pop(file, None)
            project.timestamps.pop(file, None)
            os.remove(os.path.join(self.user_path, file))
        project.id.submit += 1
        version_path = os.path.join(project_path, project.id.sub_path)
        os.makedirs(version_path, exist_ok=True)
        version.description = [f"## {project.id}",
                               comment,
                               f"### Removed files: ",
                               *[f' - {file}' for file in files],]
        project.save(project_path)
        version.save(version_path)
        
    def save(self, comment: str = ""):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        if project.id.submit == 0:
            raise MVCError("No files submitted")
        submits_to_collect = project.id.submit
        dev_path = os.path.join(project_path, get_submit_path(submits_to_collect))
        dev_version = Version.load(dev_path)
        dev_files = list_files_dir(dev_path)
        stable_path = os.path.join(project_path, get_stable_path())
        stable_version = Version.load(stable_path)
        stable_files = list_files_dir(stable_path)
        check_files = dev_files + [k for k in dev_version.include]
        rm_files = [f for f in stable_version.include if f not in check_files]
        for file in rm_files:
            stable_version.include.pop(file, None)
        rm_files = [f for f in stable_files if f not in check_files]
        for file in rm_files:
            os.remove(os.path.join(stable_path, file))
        for file in dev_files:
            src_path = os.path.join(dev_path, file)
            shutil.copy2(src_path, stable_path)
        for file, file_id in dev_version.include.items():
            src_path = os.path.join(project_path, file_id.sub_path, file)
            if file_id.submit > 0:
                shutil.copy2(src_path, stable_path)
            elif file_id.save == 0 and file_id.release > 0:
                stable_version.include[file] = file_id
        project.id.save += 1
        project.id.submit = 0
        sub_description = [f"## {project.id}",
                           comment,]
        for i in range(submits_to_collect, 0, -1):
            sub_version_path = os.path.join(project_path, get_submit_path(i))
            sub_version = Version.load(sub_version_path)
            sub_description += sub_version.description
        stable_version.description = sub_description + stable_version.description
        stable_version.save(stable_path)
        temp_path = os.path.join(project_path, "temp")
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        project.save(project_path)

    def release(self, comment: str = ""):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        if project.id.submit > 0:
            raise MVCError("Unsaved submits.")
        version_path = os.path.join(project_path, project.id.sub_path)
        version = Version.load(version_path)
        project.id.release += 1
        project.id.save = 0
        description = [f"## {project.id}",
                       comment,]
        version.description = description + version.description
        version.save(version_path)
        next_version = Version([], {})
        ref_files = os.listdir(version_path)
        ref_files.remove(".mvc")
        for file in ref_files:
            next_version.include[file] = project.id
        release_path = os.path.join(project_path, project.id.sub_path)
        shutil.move(version_path, release_path)
        os.makedirs(version_path)
        next_version.save(version_path)
        project.save(project_path)

    def load(self, project_name: str, release: int = -1) -> FileOperation:
        project, project_path = self._get_project(project_name)
        if release > 0:
            project.id = FileID(release, 0, 0)
            version_path = os.path.join(project_path, get_release_path(release))
        else:
            project.id.submit = 0
            version_path = os.path.join(project_path, project.id.sub_path)
        if not os.path.exists(version_path):
            raise MVCError("Invalid version")
        version = Version.load(version_path)
        version_files = list_files_dir(version_path)
        files_to_add = {}
        for file in version_files:
            files_to_add[file] = version_path
        for file, file_id in version.include.items():
            if file_id.release > 0:
                include_path = os.path.join(project_path, file_id.sub_path)
                files_to_add[file] = include_path
        return FileOperation(
            project_name,
            self._get_history_markdown(project),
            files_to_add,
            [])
    
    def load_finalize(self, recipe: FileOperation):
        self._execute(recipe)
        self._write_markdown(self.user_path, recipe.md)
        Workspace(recipe.project_name).save(self.user_path)

    def review(self) -> FileOperation:
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        if project.id.submit == 0:
            raise MVCError("No files submitted")
        dev_path = os.path.join(project_path, get_submit_path(project.id.submit))
        dev = Version.load(dev_path)
        dev_files = list_files_dir(dev_path)
        files_to_add = {}
        for file in dev_files:
            files_to_add[file] = dev_path
        for file, file_id in dev.include.items():
            file_path = os.path.join(project_path, file_id.sub_path)
            files_to_add[file] = file_path
        return FileOperation(
            project.name,
            self._get_history_markdown(project),
            files_to_add,
            [])
    
    def review_finalize(self, recipe: FileOperation):
        self._execute(recipe)
        self._write_markdown(self.user_path, recipe.md)

    def list_projects(self) -> dict[str, str]:
        projects_paths = os.listdir(self.base_path)
        ret = {}
        for path in projects_paths:
            project = Project.load(os.path.join(self.base_path, path))
            ret[project.name] = str(project.id)
        return ret

    def status(self) -> List[str]:
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        ret = []
        version_id = project.id
        for i in range(project.id.submit, 0, -1):
            version_id.submit = i
            version_path = os.path.join(project_path, version_id.sub_path)
            version = Version.load(version_path)
            ret += version.description
        return ret
    
    def contents(self) -> List[str]:
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        dev_path = os.path.join(project_path, project.id.sub_path)
        dev_version = Version.load(dev_path)
        dev_files = list_files_dir(dev_path)
        return dev_files + [k for k in dev_version.include]

    def changes(self) -> List[str]:
        workspace = self._get_workspace()
        project, _ = self._get_project(workspace.project)
        workspace_files = list_files_dir(self.user_path)
        changed_files = []
        for file in workspace_files:
            fpath = os.path.join(self.user_path, file)
            stamp = os.path.getmtime(fpath)
            file_is_new = file not in project.timestamps
            try:
                stamp_is_different = project.timestamps[file] != stamp
            except KeyError:
                stamp_is_different = False
            if file_is_new or stamp_is_different:
                changed_files.append(file)
        return changed_files