import argparse
import sys
import subprocess
import logging
from datetime import datetime

BRANCH_NAME_PREFIX = "feat/release-"

def get_branch_number(git_branch_a):
    branches = git_branch_a.split()
    branches = list(filter(lambda x: BRANCH_NAME_PREFIX in x, branches))

    releases = list(map(lambda x: int(x.split("-")[-1]), branches))

    if len(releases) == 0:
        return 1
    else:
        return max(releases) + 1


def main():
    parser = argparse.ArgumentParser(
        description="Determine new branch name for release manifest output."
    )
    parser.add_argument("--current_branches", help="the output of git branch -a")

    args = parser.parse_args(sys.argv[1:])

    if not args.current_branches:
        logging.debug("-------")
        logging.debug("Usage error. Run this script using the below command form:")
        logging.debug(
            "> python get_branch_name.py --current_branches <the output of git branch -a>"
        )
        logging.debug("-------")
        exit(0)

    branch_number = get_branch_number(args.current_branches)
    print(branch_number)


if __name__ == "__main__":
    main()
