import os
import shutil
from typing import List
from datetime import datetime

from mvc.helpers import Version, Project, Workspace 

class MVCError(Exception):
    def __init__(self, message):
        super().__init__(message)

class MiniVC:

    def _get_history_markdown(self, project: Project):
        md = []
        if project.submit_number > 0:
            md.append(f"## development version {project.version_major}.{project.version_minor}.{project.submit_number}" + os.linesep)
        for i in range(project.submit_number, 0, -1):
            version, version_path = self._get_version(project.name, f"sub{i}")
            for line in version.description:
                md.append(line)
        
        md.append(f"## stable version {project.version_major}.{project.version_minor}.0")
        version, version_path = self._get_version(project.name, "latest")
        for line in version.description:
            md.append(line)
        
        if project.version_major > 0:
            md.append(f"## Release version {project.version_major}.0.0")
        for i in range(project.version_major, 0, -1):
            version, version_path = self._get_version(project.name, f"ver{i}")
            for line in version.description:
                md.append(line)
        return md
    
    def _write_markdown(self, dst_path: str, md: List[str]):
        with open(dst_path, 'w') as fd:
            for line in md:
                fd.write(line + os.linesep)

    def _current_timestamp(self) -> str:
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _get_version(self, project_name: str, id: str):
        try:
            version_path = None
            if id.startswith('sub'):
                version_path = os.path.join(self.base_path, project_name, "temp", id)
            elif id.startswith('ver') or id == 'latest':
                version_path = os.path.join(self.base_path, project_name, "versions", id)
            if version_path and os.path.exists(version_path):
                version = Version.load(os.path.join(version_path, ".mvc"))
            else:
                raise MVCError("Invalid version ID.")
            return version, version_path
        except FileNotFoundError:
            raise MVCError("Invalid project name.")

    def _get_project(self, project_name):
        try:
            project_path = os.path.join(self.base_path, project_name)
            project = Project.load(os.path.join(project_path, ".mvc"))
            return project, project_path
        except FileNotFoundError:
            raise MVCError("Invalid project name.")     
    
    def _get_workspace(self):
        try:
            workspace = Workspace.load(os.path.join(self.user_path, ".mvc"))
            return workspace
        except FileNotFoundError:
            return None
        

    def __init__(self, base_path, user_path):
        self.base_path = base_path
        self.user_path = user_path

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
        project = Project(
            project_name,
            0,
            0,
            0,
            {},
        )

        # create the workspace
        workspace = Workspace(
            project=project_name
        )

        # create the version
        latest_version_path = os.path.join(project_path, "versions", "latest")
        os.makedirs(latest_version_path, exist_ok=True)
        version = Version(
            "latest",
            [
                "",
                "### Project Created",
                "",
                self._current_timestamp()
            ],
            {}
        )

        workspace.save(os.path.join(self.user_path, ".mvc"))
        project.save(os.path.join(project_path, ".mvc"))
        version.save(os.path.join(latest_version_path, ".mvc"))

    def submit(self, files: List[str], description: str):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        version, version_path = self._get_version(project.name, f"sub{project.submit_number}" if project.submit_number > 0 else "latest")
        work_files = os.listdir(version_path)
        work_files.remove('.mvc')
        for file in work_files:
            version.files[file] = version.id
        for file in files:
            version.files.pop(file, None)
        project.submit_number += 1
        version.id = f"sub{project.submit_number}"
        version_path = os.path.join(project_path, "temp", f"sub{project.submit_number}")
        os.makedirs(version_path, exist_ok=True)
        for file_name in files:
            src_path = os.path.join(self.user_path, file_name)
            dst_path = os.path.join(version_path, file_name)
            shutil.copy2(src_path, dst_path)
            project.files[file_name] = os.path.getmtime(src_path)
        version.description = [
            f"#### v{project.version_major}.{project.version_minor}.{project.submit_number}: {description}",
            f"Submitted files: {', '.join(files)}",
        ]
        version.save(os.path.join(version_path, ".mvc"))
        project.save(os.path.join(project_path, ".mvc"))

    def remove(self, files: List[str], description = ""):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        version, version_path = self._get_version(project.name, f"sub{project.submit_number}" if project.submit_number > 0 else "latest")
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
        version_path = os.path.join(project_path, "temp", version.id)
        os.makedirs(version_path, exist_ok=True)
        version.description = [
            f"#### v{project.version_major}.{project.version_minor}.{project.submit_number}: {description}",
            f"Removed files: {', '.join(files)}",
        ]
        project.save(os.path.join(project_path, ".mvc"))
        version.save(os.path.join(version_path, ".mvc"))
        
    def save(self):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        if project.submit_number == 0:
            raise MVCError("No files submitted")
        project.version_minor += 1
        dev_version, dev_version_path = self._get_version(project.name, f"sub{project.submit_number}")
        latest_version, latest_version_path = self._get_version(project.name, "latest")
        description = [
            "",
            f"### v{project.version_major}.{project.version_minor}.0: Submits saved into latest",
            "",
        ]
        work_files = os.listdir(dev_version_path)
        work_files.remove('.mvc')
        for file in work_files:
            shutil.copy2(os.path.join(dev_version_path, file), latest_version_path)
        for file, file_id in dev_version.files.items():
            if 'sub' in file_id:
                src_path = os.path.join(project_path, "temp", file_id)
                shutil.copy2(os.path.join(src_path, file), latest_version_path)
            elif 'ver' in file_id:
                latest_version.files[file] = file_id
        for i in range(project.submit_number, 0, -1):
            sub_version, _ = self._get_version(project.name, f"sub{i}")
            description += sub_version.description

        
        project.submit_number = 0
        latest_version.id = "latest"
        latest_version.description = description + latest_version.description
        latest_version.save(os.path.join(latest_version_path, '.mvc'))
        temp_path = os.path.join(project_path, "temp")
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        project.save(os.path.join(project_path, ".mvc"))

    def release(self):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        if project.submit_number > 0:
            raise MVCError("Unsaved submits.")
        project.version_major += 1
        project.version_minor = 0
        version, version_path = self._get_version(project.name, "latest")
        description = [
            "",
            f"### v{project.version_major}.{project.version_minor}.{project.submit_number}: Released",
            "",
        ]
        version.description = description + version.description
        version.id = f"ver{project.version_major}"
        version.save(os.path.join(version_path, ".mvc"))
        next_version = Version("latest", [], {})
        ref_files = os.listdir(version_path)
        ref_files.remove(".mvc")
        for file in ref_files:
            next_version.files[file] = version.id
        release_path = os.path.join(project_path, "versions", version.id)
        shutil.move(version_path, release_path)
        os.makedirs(version_path)
        next_version.save(os.path.join(version_path, ".mvc"))
        project.save(os.path.join(project_path, ".mvc"))

    def load(self, project_name: str, version_id='latest'):
        workspace = Workspace(project_name)
        project, project_path = self._get_project(workspace.project)
        version_path = os.path.join(project_path, "versions", version_id)
        if not os.path.exists(version_path):
            raise MVCError("Invalid version")
        workspace.save(os.path.join(self.user_path, ".mvc"))
        version = Version.load(os.path.join(version_path, ".mvc"))
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
        md = self._get_history_markdown(project)
        self._write_markdown(os.path.join(self.user_path, "changelog.md"), md)

    def review(self):
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)

        if project.submit_number > 0:
            version_path = os.path.join(project_path, "temp", f"sub{project.submit_number}")
        else:
            raise MVCError("No files submitted")
        version = Version.load(os.path.join(version_path, ".mvc"))
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
                raise MVCError("Invalid version ID")
            dst_path = os.path.join(self.user_path, file)
            shutil.copy2(src_path, dst_path)
        md = self._get_history_markdown(project)
        self._write_markdown(os.path.join(self.user_path, "changelog.md"), md)

    def list_projects(self) -> List[str]:
        projects_paths = os.listdir(self.base_path)
        ret = []
        for path in projects_paths:
            project = Project.load(os.path.join(self.base_path, path, ".mvc"))
            ret.append((project.name, project.version_major, project.version_minor, project.submit_number))
        return ret

    def status(self) -> List[str]:
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        ret = []
        for i in range(1, project.submit_number+1):
            version = Version.load(os.path.join(project_path, "temp", f"sub{i}", ".mvc"))
            ret += version.description
        return ret
    
    def contents(self) -> List[str]:
        workspace = self._get_workspace()
        project, project_path = self._get_project(workspace.project)
        version, version_path = self._get_version(project.name, 'latest')
        files = os.listdir(version_path)
        files.remove(".mvc")
        files += [k for k in version.files]
        return files

    def changes(self) -> List[str]:
        workspace = self._get_workspace()
        project, _ = self._get_project(workspace.project)
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