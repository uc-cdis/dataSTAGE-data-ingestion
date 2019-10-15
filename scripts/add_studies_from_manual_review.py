import argparse
import os
import sys
from datetime import datetime
from generate_google_group_cmds import dedup_study_accessions, write_list_of_strings_to_file_as_rows

def retrieve_study_accessions_from_manual_review_file(filename):
    f = open(filename)
    contents = f.readlines()
    f.close()
    headers = contents[0].split('\t')
    index_of_study_accession_column = -2
    ignore_column = -1
    try:
        index_of_study_accession_column = headers.index('study_accession')
        ignore_column = headers.index('study_accession')
    except ValueError as e:
        print("ERROR: Could not find one of ['study accession' , 'ignore'] column in tsv headers.")

    records = list(map(lambda x: x.split('\t'), contents[1:])) # First line of tsv is column names

    study_accessions_undeduped = []
    for record in records:
        if record[index_of_study_accession_column] is not None \
            and record[index_of_study_accession_column] != '' \
            and record[ignore_column].toLowerCase() != 'x':
            study_accessions_undeduped.append(record[index_of_study_accession_column].strip())

    print(study_accessions_undeduped)
    study_accessions = dedup_study_accessions(study_accessions_undeduped)
    return study_accessions

def retrieve_study_accessions_from_phs_id_list_file(filename):
    f = open(filename)
    contents = f.readlines()
    f.close()
    return map(lambda x: x.strip(), contents)

def main():
    parser = argparse.ArgumentParser(
        description="Combine a file of newline-separated PHS IDs with a manually filled out data_requiring_manual_review.tsv."
    )
    parser.add_argument(
        "--phs_id_list",
        help="text file containing newline-separated PHS IDs",
    )
    parser.add_argument(
        "--data_requiring_manual_review",
        help="tsv file from review process with missing study accessions filled out manually",
    )
    parser.add_argument(
        "--output_file",
        help="name of output file to write to",
    )

    args = parser.parse_args(sys.argv[1:])

    if not args.phs_id_list \
        or not args.data_requiring_manual_review \
        or not args.output_file:
        print("-------")
        print(
            "Usage error. Call the script like this:"
        )
        print(
            "> python3 add_studies_from_manual_review.py --phs_id_list <phs_id_list.txt> --data_requiring_manual_review <data_requiring_manual_review.tsv> --output_file <out_file.txt>"
        )
        print("-------")
        exit(0)
   
    new_study_accessions = retrieve_study_accessions_from_manual_review_file(args.data_requiring_manual_review)
    old_study_accessions = retrieve_study_accessions_from_phs_id_list_file(args.phs_id_list)

    if os.path.exists(args.output_file):
        os.remove(args.output_file)

    write_list_of_strings_to_file_as_rows(new_study_accessions + old_study_accessions, args.output_file)
    
    print("Wrote merged PHS ID list to {}.".format(
        args.output_file
    ))

if __name__ == '__main__':
    main()