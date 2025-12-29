import os
import shutil
import json
from typing import List
from datetime import datetime

class MVCError(Exception):
    def __init__(self, message):
        super().__init__(message)

class MiniVC:
    def _new_workspace(self, project_name: str):
        self.workspace = {'workspace': {'project': project_name}}
        with open(os.path.join(self._ws_path, '.mvc'), 'w') as f:
            json.dump(self.workspace, f)

    def _load_workspace(self):
        mvcpath = os.path.join(self._ws_path, '.mvc')
        if os.path.exists(mvcpath):
            with open(mvcpath, 'r') as fd:
                self.workspace = json.load(fd)
            
    def _current_timestamp(self) -> str:
        return datetime.now().isoformat()
    
    def _get_project_from_ws(self):
        if self.workspace is None:
            raise MVCError("No workspace found.")
        project_path = os.path.join(self._base_path, self.workspace["workspace"]["project"])
        if not os.path.exists(project_path):
            raise MVCError("Project does not exist.")
        return project_path
    
    def _compose_changelog(self, submit_number, project_path):
        changelog = []
        for i in range(1, submit_number+1):
            with open(os.path.join(project_path, "temp", f"sub{i}", ".mvc"), 'r') as f:
                description = json.load(f)["version"]["description"]
                changelog.append(f"Submit {i}: {description}")
        return "\n".join(changelog)
        
    def __init__(self, base_path, workspace_path):
        self._base_path = base_path
        self._ws_path = workspace_path
        self.workspace = None
        self._load_workspace()

    def create(self, project_name: str):
        if project_name == '': raise MVCError("Project must have a name.")
        self._new_workspace(project_name)
        project_path = os.path.join(self._base_path, self.workspace["workspace"]["project"])
        latest_version_path = os.path.join(project_path, "versions", "latest")
        os.makedirs(latest_version_path, exist_ok=True)
        with open(os.path.join(latest_version_path, '.mvc'), 'w') as f:
            json.dump({"version":
                       {"id": "latest",
                        "timestamp": self._current_timestamp(),
                        "description": "Initial version",
                        "files": {}}
                        }, f)
        with open(os.path.join(project_path, '.mvc'), 'w') as f:
            json.dump({"project": 
                       {"submit_number": 0,
                        "version_number": 0,
                        "files": {}}
                        }, f)

    def submit(self, files: List[str], description: str):
        project_path = self._get_project_from_ws()
        with open(os.path.join(project_path, '.mvc'), 'r') as f:
            project_data = json.load(f)["project"]
        submit_number = project_data["submit_number"]
        if submit_number > 0:
            work_path = os.path.join(project_path, "temp", f"sub{submit_number}")
        else:
            work_path = os.path.join(project_path, "versions", "latest")
        with open(os.path.join(work_path, ".mvc"), 'r') as f:
            version_data = json.load(f)["version"]
        work_files = os.listdir(work_path)
        work_files.remove('.mvc')
        if work_files is None:
            work_files = []
        for file in work_files:
            version_data['files'][file] = version_data['id']
        for file in files:
            version_data['files'].pop(file, None)
        submit_number += 1
        version_data['id'] = f"sub{submit_number}"
        version_data['description'] = description
        work_path = os.path.join(project_path, "temp", f"sub{submit_number}")
        os.makedirs(work_path, exist_ok=True)
        for file_name in files:
            src_path = os.path.join(self._ws_path, file_name)
            dst_path = os.path.join(work_path, file_name)
            shutil.copy2(src_path, dst_path)
            project_data["files"][file_name] = os.path.getmtime(src_path)
        with open(os.path.join(work_path, ".mvc"), 'w') as f:
            json.dump({"version": version_data}, f)
        project_data["submit_number"] = submit_number
        with open(os.path.join(project_path, ".mvc"), 'w') as f:
            json.dump({"project": project_data}, f)

    def save(self, description: str):
        project_path = self._get_project_from_ws()
        with open(os.path.join(project_path, '.mvc'), 'r') as f:
            project_data = json.load(f)["project"]
        submit_number = project_data["submit_number"]
        if submit_number > 0:
            work_path = os.path.join(project_path, "temp", f"sub{submit_number}")
        else:
            raise MVCError("No files submitted")
        with open(os.path.join(work_path, ".mvc"), 'r') as f:
            version_data = json.load(f)["version"]
        versioned_files = {}
        dst_path = os.path.join(project_path, "versions", "latest")
        work_files = os.listdir(work_path)
        work_files.remove('.mvc')
        for file in work_files:
            src_path = os.path.join(work_path, file)
            shutil.copy2(src_path, dst_path)
        for file, version in version_data['files'].items():
            if 'sub' in version:
                src_path = os.path.join(project_path, "temp", version, file)
                shutil.copy2(src_path, dst_path)
            elif 'ver' in version:
                versioned_files[file] = version
        with open(os.path.join(dst_path, '.mvc'), 'w') as f:
            json.dump({"version":
                       {"id": "latest",
                        "timestamp": self._current_timestamp(),
                        "description": description,
                        "files": versioned_files}
                        }, f)
        changelog = self._compose_changelog(submit_number, project_path)
        with open(os.path.join(dst_path, 'changelog.txt'), 'w') as f:
            f.write(changelog)
        temp_path = os.path.join(project_path, "temp")
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        project_data['submit_number'] = 0
        with open(os.path.join(project_path, ".mvc"), 'w') as f:
            json.dump({"project": project_data}, f)

    def release(self):
        project_path = self._get_project_from_ws()
        with open(os.path.join(project_path, '.mvc'), 'r') as f:
            project_data = json.load(f)["project"]
        if project_data["submit_number"] > 0:
            raise MVCError("Unsaved submits.")
        latest_path = os.path.join(project_path, "versions", "latest")
        with open(os.path.join(latest_path, ".mvc"), 'r') as f:
            version_data = json.load(f)["version"]
        version_number = project_data["version_number"]
        version_number += 1
        version_path = os.path.join(project_path, "versions", f"ver{version_number}")
        ref_files = os.listdir(latest_path)
        ref_files.remove(".mvc")
        if "changelog.txt" in ref_files:
            ref_files.remove("changelog.txt")
        for file in ref_files:
            version_data["files"][file] = f"ver{version_number}"
        version_data["description"] = f"Version {version_number}"
        version_data["timestamp"] = self._current_timestamp()
        shutil.move(latest_path, version_path)
        os.makedirs(latest_path)
        with open(os.path.join(latest_path, ".mvc"), 'w') as f:
            json.dump({"version": version_data}, f)
        project_data["version_number"] = version_number
        with open(os.path.join(project_path, ".mvc"), 'w') as f:
            json.dump({"project": project_data}, f)

    def load(self, project_name: str, version='latest'):
        self._new_workspace(project_name)
        project_path = self._get_project_from_ws()
        work_path = os.path.join(project_path, "versions", version)
        if not os.path.exists(work_path):
            raise MVCError("Invalid version")
        with open(os.path.join(work_path, ".mvc"), 'r') as f:
            version_data = json.load(f)["version"]
        work_files = os.listdir(work_path)
        work_files.remove('.mvc')
        for file in work_files:
            src_path = os.path.join(work_path, file)
            dst_path = os.path.join( self._ws_path, file)
            shutil.copy2(src_path, dst_path)
        for file, ver in version_data['files'].items():
            if 'ver' in ver:
                src_path = os.path.join(project_path, "versions", ver, file)
                dst_path = os.path.join( self._ws_path, file)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)

    def review(self):
        project_path = self._get_project_from_ws()
        with open(os.path.join(project_path, '.mvc'), 'r') as f:
            project_data = json.load(f)["project"]
        submit_number = project_data["submit_number"]
        if submit_number > 0:
            work_path = os.path.join(project_path, "temp", f"sub{submit_number}")
        else:
            raise MVCError("No files submitted")
        with open(os.path.join(work_path, ".mvc"), 'r') as f:
            version_data = json.load(f)["version"]
        work_files = os.listdir(work_path)
        work_files.remove('.mvc')
        for file in work_files:
            src_path = os.path.join(work_path, file)
            dst_path = os.path.join( self._ws_path, file)
            shutil.copy2(src_path, dst_path)
        for file, ver in version_data['files'].items():
            if 'sub' in ver:
                src_path = os.path.join(project_path, "temp", ver, file)
            elif 'ver' in ver:
                src_path = os.path.join(project_path, "versions", ver, file)
            else:
                continue
            dst_path = os.path.join(self._ws_path, file)
            shutil.copy2(src_path, dst_path)
        changelog = self._compose_changelog(submit_number, project_path)
        with open(os.path.join(self._ws_path, "changelog.txt"), 'w') as f:
            f.write(changelog)

    def list(self) -> str:
        projects = os.listdir(self._base_path)
        return "\n".join(projects)

    def status(self) -> str:
        project_path = self._get_project_from_ws()
        with open(os.path.join(project_path, '.mvc'), 'r') as f:
            project_data = json.load(f)["project"]
        submit_number = project_data["submit_number"]
        version_number = project_data["version_number"]
        ret = []
        with open(os.path.join(project_path, "versions", "latest", ".mvc"), 'r') as f:
            version_data = json.load(f)
            ret.append(f"Latest: {version_data['version']['description']}")
        for i in range(1, submit_number+1):
            with open(os.path.join(project_path, "temp", f"sub{i}", ".mvc"), 'r') as f:
                version_data = json.load(f)
                ret.append(f"Submit {i}: {version_data['version']['description']}")
        for i in range(1, version_number+1):
            with open(os.path.join(project_path, "versions", f"ver{i}", ".mvc"), 'r') as f:
                version_data = json.load(f)
                ret.append(f"Version {i}: {version_data['version']['description']}")
        return "\n".join(ret)
    
    def contents(self) -> str:
        project_path = self._get_project_from_ws()
        with open(os.path.join(project_path, '.mvc'), 'r') as f:
            project_data = json.load(f)["project"]
        submit_number = project_data["submit_number"]
        if submit_number > 0:
            work_path = os.path.join(project_path, "temp", f"sub{submit_number}")
        else:
            work_path = os.path.join(project_path, "versions", "latest")
        with open(os.path.join(work_path, ".mvc"), 'r') as f:
            version_data = json.load(f)["version"]
        files = os.listdir(work_path)
        files.remove(".mvc")
        files += [k for k in version_data['files']]
        return "\n".join(files)

    def remove(self, files: List[str]):
        project_path = self._get_project_from_ws()
        with open(os.path.join(project_path, '.mvc'), 'r') as f:
            project_data = json.load(f)["project"]
        submit_number = project_data["submit_number"]
        if submit_number > 0:
            work_path = os.path.join(project_path, "temp", f"sub{submit_number}")
        else:
            work_path = os.path.join(project_path, "versions", "latest")
        with open(os.path.join(work_path, ".mvc"), 'r') as f:
            version_data = json.load(f)["version"]
        work_files = os.listdir(work_path)
        work_files.remove('.mvc')
        if work_files is None:
            work_files = []
        for file in work_files:
            version_data['files'][file] = version_data['id']
        for file in files:
            version_data['files'].pop(file, None)
            project_data["files"].pop(file, None)
            os.remove(os.path.join(self._ws_path, file))
        submit_number += 1
        version_data['id'] = f"sub{submit_number}"
        version_data['description'] = f"removed {','.join(files)}"
        work_path = os.path.join(project_path, "temp", f"sub{submit_number}")
        os.makedirs(work_path, exist_ok=True)
        with open(os.path.join(work_path, ".mvc"), 'w') as f:
            json.dump({"version": version_data}, f)
        project_data["submit_number"] = submit_number
        with open(os.path.join(project_path, ".mvc"), 'w') as f:
            json.dump({"project": project_data}, f)

    def changes(self) -> str:
        project_path = self._get_project_from_ws()
        with open(os.path.join(project_path, '.mvc'), 'r') as f:
            project_data = json.load(f)["project"]
        workspace_files = os.listdir(self._ws_path)
        workspace_files.remove('.mvc')
        if workspace_files is None:
            workspace_files = []
        changed_files = []
        for file in workspace_files:
            fpath = os.path.join(self._ws_path, file)
            stamp = os.path.getmtime(fpath)
            file_is_new = file not in project_data["files"]
            try:
                stamp_is_different = project_data["files"][file] != stamp
            except KeyError:
                stamp_is_different = False
            if file_is_new or stamp_is_different:
                changed_files.append(file)
        return "\n".join(changed_files)