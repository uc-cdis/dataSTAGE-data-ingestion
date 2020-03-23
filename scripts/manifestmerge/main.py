import os
import sys
import argparse
import scripts
import csv
import utils

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--genome_manifest", required=True)
    parser.add_argument("--dbgap_extract_file", required=True)
    parser.add_argument("--studies_to_google_access_groups", required=True)
    parser.add_argument("--output", required=True)

    return parser.parse_args()


"""
python main.py 
    --genome_manifest ../input/genome_file_manifest.csv
    --dbgap_extract_file ../input/DataSTAGE_dbGaP_Consent_Extract.tsv
    --studies_to_google_access_groups studies_to_google_access_groups.txt
    --out ../output
"""
def main():
    args = parse_arguments()
    scripts.merge(args.genome_manifest, args.dbgap_extract_file, args.studies_to_google_access_groups, args.output)


if __name__ == "__main__":
    main()
