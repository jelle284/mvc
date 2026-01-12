import os
import shutil
from typing import List
from datetime import datetime

from mvc.helpers import MVCProject, MVCVersion, MVCWorkspace

class MVCError(Exception):
    def __init__(self, message):
        super().__init__(message)

class MiniVC:
    def _get_history_markdown(self, project: MVCProject, dst_path: str):
        history = project.history
        history.append([
            f"# lastest version {project.version_major}.{project.version_minor}.{project.submit_number}",
        ])
        with open(dst_path, 'w') as fd:
            for item in reversed(project.history):
                item: list[str]
                for line in item:
                    fd.write(line + os.linesep)
    
    def _current_timestamp(self) -> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _get_version(self, project: MVCProject):
        try:
            if project.submit_number > 0:
                version_path = os.path.join(self.base_path, project.name, "temp", f"sub{project.submit_number}")
            else:
                version_path = os.path.join(self.base_path, project.name, "versions", "latest")
            version = MVCVersion.load(os.path.join(version_path, ".mvc"))
            return version, version_path
        except FileNotFoundError:
            raise MVCError("Invalid project.")
    
    def _get_project(self, workspace: MVCWorkspace):
        try:
            project_path = os.path.join(self.base_path, workspace.project)
            project = MVCProject.load(os.path.join(project_path, ".mvc"))
            return project, project_path
        except FileNotFoundError:
            raise MVCError("Invalid Workspace Configuration.")     
    
    def _get_workspace(self):
        try:
            workspace = MVCWorkspace.load(os.path.join(self.user_path, ".mvc"))
            return workspace
        except FileNotFoundError:
            return None
        

    def __init__(self, base_path, user_path):
        # store args
        self.base_path = base_path
        self.user_path = user_path

        # check if the base path exists, otherwise make it
        if not os.path.exists(base_path):
            raise MVCError("Invalid base path.")

    def create(self, project_name: str):
        # check args
        if project_name == '': raise MVCError("Project must have a name.")

        # create the project directory
        project_path = os.path.join(self.base_path, project_name)
        try:
            os.makedirs(project_path)
        except OSError:
            raise MVCError("Trying to create project which already exists.")
        
        # create the project
        project = MVCProject(
            project_name,
            0,
            0,
            0,
            {},
            []
        )

        # create the workspace
        workspace = MVCWorkspace(
            project=project_name
        )

        # create the version
        latest_version_path = os.path.join(project_path, "versions", "latest")
        os.makedirs(latest_version_path, exist_ok=True)
        version = MVCVersion(
            "latest",
            self._current_timestamp(),
            "Project created",
            {}
        )

        # record and save
        project.history.append([
            "# Project Created",
            self._current_timestamp(),
        ])
        workspace.save(os.path.join(self.user_path, ".mvc"))
        project.save(os.path.join(project_path, ".mvc"))
        version.save(os.path.join(latest_version_path, ".mvc"))

    def submit(self, files: List[str], description: str):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace)
        version, version_path = self._get_version(project)
        work_files = os.listdir(version_path)
        work_files.remove('.mvc')
        for file in work_files:
            version.files[file] = version.id
        for file in files:
            version.files.pop(file, None)
        project.submit_number += 1
        version.id = f"sub{project.submit_number}"
        version.description = description
        version_path = os.path.join(project_path, "temp", f"sub{project.submit_number}")
        os.makedirs(version_path, exist_ok=True)
        for file_name in files:
            src_path = os.path.join(self.user_path, file_name)
            dst_path = os.path.join(version_path, file_name)
            shutil.copy2(src_path, dst_path)
            project.files[file_name] = os.path.getmtime(src_path)
        project.history.append([
            f"**Submit:** {version.description}",
            f"{', '.join(files)}",
        ])
        version.save(os.path.join(version_path, ".mvc"))
        project.save(os.path.join(project_path, ".mvc"))

    def remove(self, files: List[str], description = ""):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace)
        version, version_path = self._get_version(project)
        work_files = os.listdir(version_path)
        work_files.remove('.mvc')
        for file in work_files:
            version.files[file] = version.id
        for file in files:
            version.files.pop(file, None)
            project.files.pop(file, None)
            os.remove(os.path.join(self.user_path, file))
        project.submit_number += 1
        version.id = f"sub{project.submit_number}"
        version.description = description
        version_path = os.path.join(project_path, "temp", version.id)
        os.makedirs(version_path, exist_ok=True)
        project.history.append([
            f"**Remove:** {version.description}",
            f"{', '.join(files)}",
        ])
        project.save(os.path.join(project_path, ".mvc"))
        version.save(os.path.join(version_path, ".mvc"))
        
    def save(self, description: str):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace)
        if project.submit_number == 0:
            raise MVCError("No files submitted")
        submitted_version, submitted_version_path = self._get_version(project)
        latest_version_path = os.path.join(project_path, "versions", "latest")
        latest_version = MVCVersion.load(os.path.join(latest_version_path, ".mvc"))
        work_files = os.listdir(submitted_version_path)
        work_files.remove('.mvc')
        for file in work_files:
            shutil.copy2(os.path.join(submitted_version_path, file), latest_version_path)
        for file, file_id in submitted_version.files.items():
            if 'sub' in file_id:
                src_path = os.path.join(project_path, "temp", file_id)
                shutil.copy2(os.path.join(src_path, file), latest_version_path)
            elif 'ver' in file_id:
                latest_version.files[file] = file_id
        project.version_minor += 1
        latest_version.id = "latest"
        latest_version.timestamp = self._current_timestamp()
        latest_version.description = description
        latest_version.save(os.path.join(latest_version_path, '.mvc'))
        temp_path = os.path.join(project_path, "temp")
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        project.history.append([
            f"**Project saved**: {description}",
        ])
        project.submit_number = 0
        project.save(os.path.join(project_path, ".mvc"))

    def release(self):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace)
        if project.submit_number > 0:
            raise MVCError("Unsaved submits.")
        version, version_path = self._get_version(project)
        project.version_major += 1
        ref_files = os.listdir(version_path)
        ref_files.remove(".mvc")
        for file in ref_files:
            version.files[file] = f"ver{project.version_major}"
        release_path = os.path.join(project_path, "versions", f"ver{project.version_major}")
        version.description = "Released"
        version.timestamp = self._current_timestamp()
        shutil.move(version_path, release_path)
        os.makedirs(version_path)
        project.version_minor = 0
        project.history.append([
            f"# v{project.version_major}.{project.version_minor}.{project.submit_number}",
        ])
        version.save(os.path.join(version_path, ".mvc"))
        project.save(os.path.join(project_path, ".mvc"))

    def load(self, project_name: str, version_id='latest'):
        workspace = MVCWorkspace(project_name)
        project, project_path = self._get_project(workspace)
        version_path = os.path.join(project_path, "versions", version_id)
        if not os.path.exists(version_path):
            raise MVCError("Invalid version")
        workspace.save(os.path.join(self.user_path, ".mvc"))
        version = MVCVersion.load(os.path.join(version_path, ".mvc"))
        work_files = os.listdir(version_path)
        work_files.remove('.mvc')
        for file in work_files:
            src_path = os.path.join(version_path, file)
            dst_path = os.path.join(self.user_path, file)
            shutil.copy2(src_path, dst_path)
        for file, file_id in version.files.items():
            if 'ver' in file_id:
                src_path = os.path.join(project_path, "versions", file_id, file)
                dst_path = os.path.join(self.user_path, file)
                shutil.copy2(src_path, dst_path)
        self._get_history_markdown(project, os.path.join(self.user_path, "changelog.md"))

    def review(self):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace)

        if project.submit_number > 0:
            version_path = os.path.join(project_path, "temp", f"sub{project.submit_number}")
        else:
            raise MVCError("No files submitted")
        version = MVCVersion.load(os.path.join(version_path, ".mvc"))
        work_files = os.listdir(version_path)
        work_files.remove('.mvc')
        for file in work_files:
            src_path = os.path.join(version_path, file)
            dst_path = os.path.join(self.user_path, file)
            shutil.copy2(src_path, dst_path)
        for file, file_id in version.files.items():
            if 'sub' in file_id:
                src_path = os.path.join(project_path, "temp", file_id, file)
            elif 'ver' in file_id:
                src_path = os.path.join(project_path, "versions", file_id, file)
            else:
                continue
            dst_path = os.path.join(self.user_path, file)
            shutil.copy2(src_path, dst_path)
        self._get_history_markdown(project, os.path.join(self.user_path, "changelog.md"))

    def list(self) -> str:
        projects = os.listdir(self.base_path)
        return projects

    def status(self) -> str:
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace)
        ret = []
        version = MVCVersion.load(os.path.join(project_path, "versions", "latest", ".mvc"))
        ret.append(f"Latest: {version.description}")
        for i in range(1, project.submit_number+1):
            version = MVCVersion.load(os.path.join(project_path, "temp", f"sub{i}", ".mvc"))
            ret.append(f"Submit {i}: {version.description}")
        for i in range(1, project.version_major+1):
            version = MVCVersion.load(os.path.join(project_path, "versions", f"ver{i}", ".mvc"))
            ret.append(f"Version {i}: {version.description}")
        return ret
    
    def contents(self) -> str:
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace)
        version, version_path = self._get_version(project)
        files = os.listdir(version_path)
        files.remove(".mvc")
        files += [k for k in version.files]
        return files

    def changes(self) -> List[str]:
        workspace = self._get_workspace()
        project, _ = self._get_project(workspace)
        workspace_files = os.listdir(self.user_path)
        workspace_files.remove('.mvc')
        changed_files = []
        for file in workspace_files:
            fpath = os.path.join(self.user_path, file)
            stamp = os.path.getmtime(fpath)
            file_is_new = file not in project.files
            try:
                stamp_is_different = project.files[file] != stamp
            except KeyError:
                stamp_is_different = False
            if file_is_new or stamp_is_different:
                changed_files.append(file)
        return changed_files