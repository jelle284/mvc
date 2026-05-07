# mvc
Mini Version Control

## About
This is a simple version control system targeting binary files or formats otherwise unsuitable for git-diffs. It was originally intended for FreeCAD models.

A version is marked with three numbers:\
{major}.{minor}.{dev}

- Major represents archived releases.
- Minor represents reviewed and working (functioning) point.
- Dev represents steps in the development.

Projects are stored in a managed directory, which is just a plain folder. This can be on a shared folder, Dropbox, OneDrive or similar. This is referred to as the base path.

The current working directory, where the user files are, is referred to as the workspace.

## Install
When installed, the package provides a command line interface with the "mvc" command. See

    mvc -h

The CLI looks for an environment variable `MVC_BASE_PATH` for the directory to store projects. If not found, it defaults to `C:/Users/<username>/mvc-files`.
If the base path doesn't exist, it raises an error.

## Commands

### Create
Creates an empty project in the base path.
```bash
mvc create my_project
```
### Load
Sets an existing project as active in the current workspace. It does not transfer any files.
```bash
mvc load my_project
```
### Collect
Collects all files from a project and transfers them to the workspace.
```bash
mvc collect
```
### Submit
Submits one or more files into the project and increments the dev version.
```bash
mvc submit file1.bin file2.bin --description "Update model files"
```
### Remove
Removes a file from the project.
```bash
mvc remove file1.bin --description "Remove obsolete file"
```
### Accept
Accepts all submitted files into the project.
- Minor version is incremented
- Files from previous dev versions can no longer be collected.
- Later submits will overwrite earlier ones if they have the same filename.
- Previous minor version is overwritten. 
To revert to previous versions, collect the files from that version and submit them again to overwrite.
```bash
mvc accept --description "Accept submitted files"
```
### Release
Creates a permanent release version of the current project. If there are submits pending, it throws an error.
```bash
mvc release --description "Create release"
```
### Claim
Claim one or more files as belonging to the current username. This prevents others from submitting the same filename.
```bash
mvc claim file1.bin file2.bin
```
### Unclaim
Unclaims one or more files
```bash
mvc unclaim file1.bin file2.bin
```
### Get claims
Lists the files that are currently claimed with usernames.
```bash
mvc get_claims
```
### Changes
Compares the workspace to the project and lists the added and changed files.
```bash
mvc changes
```
### List
Lists the projects that exist in the base path.
```bash
mvc list
```
### Status
Prints a status message for the active project.
```bash
mvc status
```
