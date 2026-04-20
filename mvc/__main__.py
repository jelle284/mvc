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
    parser_load.add_argument("--version", type=int, default=-1, help="Version to load")

    # submit
    parser_submit = subparsers.add_parser("submit", help="Submit changes")
    parser_submit.add_argument("files", nargs='+', help="Files to submit")
    parser_submit.add_argument("--description", "-d", help="Description for this submit")

    # accept
    parser_accept = subparsers.add_parser("accept", help="Accept changes")
    parser_accept.add_argument("--description", "-d", help="Description for this version")

    # release
    parser_release = subparsers.add_parser("release", help="Release a project version")
    parser_release.add_argument("--description", "-d", help="Description for this release")

    # review
    parser_review = subparsers.add_parser("review", help="Review submitted files")

    # restore
    parser_restore = subparsers.add_parser("restore", help="Restore to a previous submit")
    parser_restore.add_argument("--submit", "-s", type=int, required=True, help="Submit number to restore to")

    # remove
    parser_remove = subparsers.add_parser("remove", help="Remove files from submission")
    parser_remove.add_argument("files", nargs='+', help="Files to remove")
    parser_remove.add_argument("--description", "-d", help="Description for this removal")

    # claim
    parser_claim = subparsers.add_parser("claim", help="Claim files for editing")
    parser_claim.add_argument("files", nargs='+', help="Files to claim")

    # unclaim
    parser_unclaim = subparsers.add_parser("unclaim", help="Unclaim files")
    parser_unclaim.add_argument("files", nargs='+', help="Files to unclaim")
    parser_unclaim.add_argument("--force", action="store_true", help="Force unclaim even if claimed by others")

    # changes
    parser_changes = subparsers.add_parser("changes", help="Get list of changed files")

    # contents
    parser_contents = subparsers.add_parser("contents", help="Get project contents")

    # get_claims
    parser_get_claims = subparsers.add_parser("get_claims", help="Get file claims")

    # list
    parser_list = subparsers.add_parser("list", help="Get a list of projects")

    # status
    parser_status = subparsers.add_parser("status", help="Get the versions and submits in the project")

    args = parser.parse_args()
    
    # Get username from environment variables
    user_name = os.getenv('USER') or os.getenv('USERNAME') or 'unknown'
    mvc = MiniVC(os.getenv('MINIVC_BASE_PATH', 'mvc-files'), os.getcwd(), user_name)
    
    # parse commands
    try:
        if args.command == "submit":
            description = args.description or "no description"
            mvc.submit(args.files, description)
            print("Files submitted successfully")
        
        elif args.command == "accept":
            description = args.description or "no description"
            mvc.accept(description)
            print("Changes accepted successfully")
        
        elif args.command == "release":
            description = args.description or "no description"
            mvc.release(description)
            print("Project released successfully")
        
        elif args.command == "create":
            mvc.create(args.project)
            print(f"Project '{args.project}' created successfully")
        
        elif args.command == 'list':
            projects = mvc.list_projects()
            for name, version in projects.items():
                print(f"{name}: {version}")
        
        elif args.command == "load":
            recipe = mvc.load(args.project, args.version)
            print("Loading files:", ", ".join(recipe.files_to_add.keys()) if recipe.files_to_add else "none")
            if prompt_confirm("Apply changes?"):
                mvc.load_finalize(recipe)
                print("Files loaded successfully")
            else:
                print("Operation cancelled")
        
        elif args.command == 'status':
            status = mvc.status()
            for line in status:
                print(line)
        
        elif args.command == "review":
            recipe = mvc.review()
            print("Reviewing files:", ", ".join(recipe.files_to_add.keys()) if recipe.files_to_add else "none")
            if prompt_confirm("Apply changes?"):
                mvc.review_finalize(recipe)
                print("Review completed successfully")
            else:
                print("Operation cancelled")
        
        elif args.command == "restore":
            recipe = mvc.restore(args.submit)
            print("Restoring files:", ", ".join(recipe.files_to_add.keys()) if recipe.files_to_add else "none")
            if prompt_confirm("Apply changes?"):
                mvc.restore_finalize(recipe)
                print("Files restored successfully")
            else:
                print("Operation cancelled")
        
        elif args.command == "remove":
            description = args.description or "no description"
            mvc.remove(args.files, description)
            print("Files removed successfully")
        
        elif args.command == "claim":
            mvc.claim(args.files)
            print("Files claimed successfully")
        
        elif args.command == "unclaim":
            mvc.unclaim(args.files, args.force)
            print("Files unclaimed successfully")
        
        elif args.command == "changes":
            changes = mvc.changes()
            if changes:
                for file in changes:
                    print(file)
            else:
                print("No changes detected")
        
        elif args.command == "contents":
            contents = mvc.contents()
            if contents:
                for file in contents:
                    print(file)
            else:
                print("Project is empty")
        
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
