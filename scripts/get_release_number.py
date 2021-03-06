import argparse
import sys
import subprocess
import logging
from datetime import datetime

BRANCH_NAME_PREFIX = "feat/release-"


def get_branch_number(git_branch_a):
    """
    Get smallest unused release number to create a new branch/directory name with
    Args:
        git_branch_a (str): the output of `git branch -a`
    Returns:
        branch number (int): the branch/relese number to use
    """
    if not git_branch_a:
        logging.debug("-------")
        logging.debug("Usage error. Run this script using the below command form:")
        logging.debug(
            "> python get_branch_name.py --current_branches <the output of git branch -a>"
        )
        logging.debug("-------")
        exit(0)
    
    branches = git_branch_a.split()
    branches = [branch for branch in branches if BRANCH_NAME_PREFIX in branch]

    releases = [int(branch.split("-")[-1]) for branch in branches]

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

    branch_number = get_branch_number(args.current_branches)
    print(branch_number)


if __name__ == "__main__":
    main()
