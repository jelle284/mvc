import os
import shutil
import json
from dataclasses import dataclass, asdict
# ================================================================= #
# ------------------------  Error classes -------------------------- #
class MVCError(Exception):
    def __init__(self, message):
        super().__init__(message)

# ================================================================= #
# ---------------------------- Functions -------------------------- #

def get_submit_path(submit_id: int) -> str:
    return os.path.join("temp", f"sub{submit_id}")

def get_stable_path() -> str:
    return os.path.join("versions", "latest")

def get_release_path(release_id: int) -> str:
    return os.path.join("versions", f"ver{release_id}")

def list_files_dir(dir: str):
    return [f for f in os.listdir(dir) if f not in (".mvc", "changelog.md")]

# ================================================================= #
# ------------------------  Data classes -------------------------- #
@dataclass
class FileID:
    release: int
    save: int
    submit: int
    def __str__(self):
        return f"v{self.release}.{self.save}.{self.submit}"
    @property
    def sub_path(self):
        if self.submit > 0:
            subpath = get_submit_path(self.submit)
        elif self.save > 0:
            subpath = get_stable_path()
        elif self.release > 0:
            subpath = get_release_path(self.release)
        else:
            subpath = get_stable_path()
        return subpath
    @classmethod
    def copy(cls, other):
        return cls(**other.__dict__)

@dataclass
class FileOperation:
    project_name: str
    md: list[str]
    files_to_add: dict[str,str]
    files_to_remove: list[str]
# ================================================================= #
# ------------------ Persistent Data classes ---------------------- #

class JSONBase:
    """Base class providing JSON persistence for dataclasses."""

    def save(self, filedir: str):
        filename = os.path.join(filedir, ".mvc")
        data = asdict(self)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load(cls, filedir: str):
        def object_hook(d: dict):
            if all(field in d for field in FileID.__annotations__):
                return FileID(**d)
            return d
        filename = os.path.join(filedir, ".mvc")
        with open(filename, 'r') as f:
            data = json.load(f, object_hook=object_hook)
        return cls(**data)

@dataclass
class Project(JSONBase):
    name: str
    id: FileID
    timestamps: dict[str, str]

@dataclass
class Workspace(JSONBase):
    project: str

@dataclass
class Version(JSONBase):
    description: list[str]
    include: dict[str, FileID]
