import os
import argparse
from .core import MiniVC, MVCError

def main():
    parser = argparse.ArgumentParser(description="miniVC CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    parser_create = subparsers.add_parser("create", help="Create a new project")
    parser_create.add_argument("project", help="Project name")

    # load
    parser_load = subparsers.add_parser("load", help="Load a project")
    parser_load.add_argument("project", help="Project name")
    parser_load.add_argument("--version", default="latest", help="Version to load (default: latest)")

    # submit
    parser_submit = subparsers.add_parser("submit", help="Submit changes")
    parser_submit.add_argument("files", nargs='+', help="Files to submit")
    parser_submit.add_argument("--description", "-d", help="Description for this submit")

    # save
    parser_save = subparsers.add_parser("save", help="Save changes")
    parser_save.add_argument("--description", "-d", help="Description for this version")

    # release
    parser_release = subparsers.add_parser("release", help="Release a project version")

    # review
    parser_review = subparsers.add_parser("review", help="Review submitted files")

    # list
    parser_list = subparsers.add_parser("list", help="Get a list of projects")

    # status
    parser_status = subparsers.add_parser("status", help="Get the versions and submits in the project")

    args = parser.parse_args()
    
    mvc = MiniVC(os.getenv('MINIVC_BASE_PATH', 'mvc-files'), os.getcwd())
    # parse commands
    if args.command == "submit":
        description = args.description or "no description"
        mvc.submit(args.files, description)
    
    elif args.command == "save":
        description = args.description or "no description"
        mvc.save(description)
    
    elif args.command == "release":
        mvc.release()
    
    if args.command == "create":
        mvc.create(args.project)
    
    elif args.command == 'list':
        print(mvc.list())

    elif args.command == "load":
        mvc.load(args.project, args.version)

    elif args.command == 'status':
        print(mvc.status())

    elif args.command == "review":
        mvc.review()
    
if __name__ == "__main__":
    try:
        main()
    except MVCError as e:
        print("Error:", e)
