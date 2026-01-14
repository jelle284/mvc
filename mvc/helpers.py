import json
from dataclasses import dataclass, asdict

class JSONBase:
    """Base class providing JSON persistence for dataclasses."""
    
    def save(self, filename: str):
        # asdict() works on instances of any class inheriting from a dataclass
        data = asdict(self)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load(cls, filename: str):
        with open(filename, 'r') as f:
            data = json.load(f)
        # Returns a new instance of the child class
        return cls(**data)

# ================================================================= #
# ------------------------  Data classes -------------------------- #

@dataclass
class Project(JSONBase):
    name: str
    submit_number: int
    version_major: int
    version_minor: int
    files: dict[str, str]

@dataclass
class Workspace(JSONBase):
    project: str

@dataclass
class Version(JSONBase):
    id: str
    description: list[str]
    files: dict[str, str]