# mvc
Mini Version Control

## About
This is a simple version control system targeting binary files or formats otherwise unsuitable for git-diffs. It was originally intended for FreeCAD models.

A version is marked with three numbers:\
{major}.{minor}.{dev}

- Major represents archived releases.
- Minor represents reviewed and working (functioning) point.
- Dev represents steps in the development.

## Intended workflow
- A new project is created or an existing one is loaded.
- Files are submitted to the project. Each submit increments the dev count. The submitted files can be recovered until they are accepted into the project.
- At any point, the submitted files can be accepted into the project. This collapses the directory in to a "latest" version, and increments the minor count. Files submitted multiple times will be overwritten with the one last submitted.
- The project can be released in its current state. This will be permanently stored and can be recovered at any time.
- Files can be claimed, meaning other users are prevented from submitting files with the same filename.
