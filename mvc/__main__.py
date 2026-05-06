import os
import argparse
from .core import MiniVC, MVCError

def prompt_confirm(message: str = "Proceed?") -> bool:
    """Prompt user for Y/n confirmation."""
    response = input(f"{message} (Y/n): ").strip().lower()
    return response != 'n'

def main():
    parser = argparse.ArgumentParser(description="miniVC CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    parser_create = subparsers.add_parser("create", help="Create a new project")
    parser_create.add_argument("project", help="Project name")

    # load
    parser_load = subparsers.add_parser("load", help="Load a project")
    parser_load.add_argument("project", help="Project name")

    # collect
    parser_collect = subparsers.add_parser("collect", help="Collect files from the project")
    
    # submit
    parser_submit = subparsers.add_parser("submit", help="Submit changes")
    parser_submit.add_argument("files", nargs='+', help="Files to submit")
    parser_submit.add_argument("--description", "-d", help="Description for this submit")

    # remove
    parser_remove = subparsers.add_parser("remove", help="Remove files from submission")
    parser_remove.add_argument("files", nargs='+', help="Files to remove")
    parser_remove.add_argument("--description", "-d", help="Description for this removal")

    # accept
    parser_accept = subparsers.add_parser("accept", help="Accept changes")
    parser_accept.add_argument("--description", "-d", help="Description for this version")

    # release
    parser_release = subparsers.add_parser("release", help="Release a project version")
    parser_release.add_argument("--description", "-d", help="Description for this release")

    # claim
    parser_claim = subparsers.add_parser("claim", help="Claim files for editing")
    parser_claim.add_argument("files", nargs='+', help="Files to claim")

    # unclaim
    parser_unclaim = subparsers.add_parser("unclaim", help="Unclaim files")
    parser_unclaim.add_argument("files", nargs='+', help="Files to unclaim")
    parser_unclaim.add_argument("--force", action="store_true", help="Force unclaim even if claimed by others")

    # get_claims
    parser_get_claims = subparsers.add_parser("get_claims", help="Get file claims")

    # changes
    parser_changes = subparsers.add_parser("changes", help="Get list of changed files")

    # contents
    parser_contents = subparsers.add_parser("contents", help="Get project contents")

    # list
    parser_list = subparsers.add_parser("list", help="Get a list of projects")

    # status
    parser_status = subparsers.add_parser("status", help="Get the versions and submits in the project")

    args = parser.parse_args()
    
    # Get username from environment variables
    user_name = os.getenv('USER') or os.getenv('USERNAME') or 'unknown'
    base_path = os.getenv('MINIVC_BASE_PATH', os.path.join('C:', 'Users', user_name, 'mvc-files'))
    user_path = os.getcwd()
    mvc = MiniVC(base_path, user_path, user_name)
    
    # parse commands
    try:
        if args.command == "create":
            mvc.create(args.project)
            print(f"Project '{args.project}' created successfully")

        elif args.command == "load":
            mvc.load(args.project)
            print(f"Project loaded successfully")

        elif args.command == "submit":
            mvc.submit(args.files, args.description or "")
            print("Files submitted successfully")
        
        elif args.command == "remove":
            mvc.remove(args.files, args.description or "")
            print("Files removed successfully")

        elif args.command == "accept":
            mvc.accept(args.description or "")
            print("Changes accepted successfully")
        
        elif args.command == "release":
            mvc.release(args.description or "")
            print("Project released successfully")

        elif args.command == 'list':
            projects = mvc.list_projects()
            for name, version in projects.items():
                print(f"{name}: {version}")
        
        elif args.command == 'status':
            status = mvc.status()
            for line in status:
                print(line)
        
        elif args.command == "collect":
            available = mvc.available()
            print("Select version to collect:")
            for i, a in enumerate(available):
                print(f"{i+1}) {a}")
            i = int(input("Enter a number: ")) - 1
            new_files, overwritten_files = mvc.changes(available[i])
            result = 0
            if overwritten_files:
                result = 1
                print("Files:", ", ".join(overwritten_files), "will be overwritten.")
                if prompt_confirm("Continue?"): result = 2
            if result == 2:
                mvc.collect(available[i])
                print("Collected files successfully")
            elif result == 1:
                print("Operation cancelled")
            else:
                print("Up to date. No files collected.")
        
        elif args.command == "claim":
            mvc.claim(args.files)
            print("Files claimed successfully")
        
        elif args.command == "unclaim":
            mvc.unclaim(args.files, args.force)
            print("Files unclaimed successfully")
        
        elif args.command == "changes":
            new_files, changed_files = mvc.changes()
            if new_files:
                print("Added:")
                for file in new_files:
                    print("+", file)
            if changed_files:
                print("Changed:")
                for file in changed_files:
                    print("*", file)
            if not changed_files and not new_files:
                print("No changes detected")
        
        elif args.command == "get_claims":
            claims = mvc.get_claims()
            if claims:
                for file, user in claims.items():
                    print(f"{file}: claimed by {user}")
            else:
                print("No files claimed")
    
    except MVCError as e:
        print("Error:", e)
    
if __name__ == "__main__":
    main()
