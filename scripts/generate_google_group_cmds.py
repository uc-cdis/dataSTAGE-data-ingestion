import argparse
import sys
import subprocess
import logging
import os
from datetime import datetime

GOOGLE_GROUPS_OUTFILE = "google-groups.sh"
MAPPING_OUTFILE = "mapping.txt"
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def generate_cmd_sets(studies):
    commands = []
    for study_accession_with_consent in studies:
        link_external_bucket_cmd = "fence-create link-external-bucket --bucket-name {}".format(
            study_accession_with_consent
        )
        commands.append(link_external_bucket_cmd)

    for study_accession_with_consent in studies:
        link_to_gen3_project_cmd = "fence-create link-bucket-to-project --bucket_id {} --bucket_provider google --project_auth_id {}".format(
            study_accession_with_consent, study_accession_with_consent
        )
        commands.append(link_to_gen3_project_cmd)

    for study_accession_with_consent in studies:
        link_to_topmed_cmd = "fence-create link-bucket-to-project --bucket_id {} --bucket_provider google --project_auth_id topmed".format(
            study_accession_with_consent, study_accession_with_consent
        )
        commands.append(link_to_topmed_cmd)

    for study_accession_with_consent in studies:
        link_all_projects_cmd = "fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id {}".format(
            study_accession_with_consent, study_accession_with_consent
        )
        commands.append(link_all_projects_cmd)

    return commands

def make_mapping_entries(study_accessions):
    entries = []
    for study in study_accessions:
        entries.append(
            "{}: stagedcp_{}_read_gbag@dcp.bionimbus.org".format(study, study)
        )
    return entries

def dedup_study_accessions(study_accessions):
    dict_of_things = {}
    for thing in study_accessions:
        if "phs" not in thing:
            continue
        dict_of_things[thing.strip()] = 1
    rv = list(dict_of_things.keys())
    rv.sort()
    return rv

def retrieve_study_accessions_from_extract(extract_filename):
    # Retrieve study_with_consent in a column-order-agnostic way
    with open(extract_filename) as f: 
        rows = f.readlines()
        headers = rows[0].split("\t")
        records = list(map(lambda x: x.split("\t"), rows[1:]))
        records_as_dicts = []
        for record in records:
            record_dict = {}
            for i in range(len(record)):
                record_dict[headers[i]] = record[i]
            records_as_dicts.append(record_dict)

        undeduped_study_accessions = list(map(lambda x: x['study_with_consent'], records_as_dicts))
        study_accessions = dedup_study_accessions(undeduped_study_accessions)
        return study_accessions

def write_list_of_strings_to_file_as_rows(array_in, output_filename):
    with open(output_filename, "a+") as out_file:
        out_file.write("\n".join(array_in))

def main():
    parser = argparse.ArgumentParser(
        description="Generate set of fence-create commands for study-related Google Groups."
    )
    parser.add_argument("--extract_filename", help="a generated dbgap extract file")

    args = parser.parse_args(sys.argv[1:])

    if not args.extract_filename:
        logging.debug("-------")
        logging.debug("Usage error. Run this script using the below command form:")
        logging.debug(
            "> python generate_google_group_cmds.py --extract_filename <filename.tsv>"
        )
        logging.debug("-------")
        exit(0)

    study_accessions = retrieve_study_accessions_from_extract(args.extract_filename)

    if os.path.exists(MAPPING_OUTFILE):
        os.remove(MAPPING_OUTFILE)
    mapping_entries = make_mapping_entries(study_accessions)
    write_list_of_strings_to_file_as_rows(mapping_entries, MAPPING_OUTFILE)

    if os.path.exists(GOOGLE_GROUPS_OUTFILE):
        os.remove(GOOGLE_GROUPS_OUTFILE)
    commands = generate_cmd_sets(study_accessions)
    write_list_of_strings_to_file_as_rows(commands, GOOGLE_GROUPS_OUTFILE)

    logging.debug(
        "Wrote commands to {}. Wrote mapping file to {}.".format(
            GOOGLE_GROUPS_OUTFILE, MAPPING_OUTFILE
        )
    )

if __name__ == "__main__":
    main()
