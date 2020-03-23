import argparse
import os
import sys
from datetime import datetime
import csv
from generate_google_group_cmds import (
    dedup_study_accessions,
    write_list_of_strings_to_file_as_rows,
)


def retrieve_study_accessions_from_manual_review_file(filename):
    """
    Obtains a list of study accession strings from a "data_requiring_manual_review.tsv" file.
    Just takes the study accession column and dedups it.
    Args:
        filename (string) 
    Returns:
        study_accessions (list of strings)
    """
    study_accessions_undeduped = []
    with open(filename, "rU") as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        rownum = 0
        for row in rd:
            if rownum == 0:
                index_of_study_accession_column = -2
                ignore_column = -1
                try:
                    index_of_study_accession_column = row.index("study_accession")
                    ignore_column = row.index("study_accession")
                except ValueError as e:
                    print(
                        "ERROR: Could not find one of ['study accession' , 'ignore'] column in tsv headers."
                    )
            else:
                if (
                    row[index_of_study_accession_column] is not None
                    and row[index_of_study_accession_column] != ""
                    and row[ignore_column].lower() != "x"
                ):
                    study_accessions_undeduped.append(
                        row[index_of_study_accession_column].strip()
                    )
            rownum += 1

    study_accessions = dedup_study_accessions(study_accessions_undeduped)
    return study_accessions


def retrieve_study_accessions_from_phs_id_list_file(filename):
    """
    Obtains a list of study accession strings from a "phs_id_list.txt" file,
    which is a newline-separated list of phs ids.
    Args:
        filename (string) 
    Returns:
        study_accessions (list of strings)
    """
    with open(filename) as f:
        contents = f.readlines()
        return list(map(lambda x: x.strip(), contents))


def add_studies_from_manual_review(phs_id_list, data_requiring_manual_review, output_file):
    if (
        not phs_id_list
        or not data_requiring_manual_review
        or not output_file
    ):
        print("-------")
        print("Usage error. Call the script like this:")
        print(
            "> python3 add_studies_from_manual_review.py --phs_id_list <phs_id_list.txt> --data_requiring_manual_review <data_requiring_manual_review.tsv> --output_file <out_file.txt>"
        )
        print("-------")
        exit(0)

    new_study_accessions = retrieve_study_accessions_from_manual_review_file(
        data_requiring_manual_review
    )
    old_study_accessions = retrieve_study_accessions_from_phs_id_list_file(
        phs_id_list
    )

    if os.path.exists(output_file):
        os.remove(output_file)

    write_list_of_strings_to_file_as_rows(
        new_study_accessions + old_study_accessions, output_file
    )

    print("Wrote merged PHS ID list to {}.".format(output_file))


def main():
    parser = argparse.ArgumentParser(
        description="Combine a file of newline-separated PHS IDs with a manually filled out data_requiring_manual_review.tsv."
    )
    parser.add_argument(
        "--phs_id_list", help="text file containing newline-separated PHS IDs"
    )
    parser.add_argument(
        "--data_requiring_manual_review",
        help="tsv file from review process with missing study accessions filled out manually",
    )
    parser.add_argument("--output_file", help="name of output file to write to")

    args = parser.parse_args(sys.argv[1:])

    add_studies_from_manual_review(args.phs_id_list, args.data_requiring_manual_review, args.output_file)

if __name__ == "__main__":
    main()
