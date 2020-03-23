import argparse
import sys
import subprocess
import logging
import os
from datetime import datetime

GOOGLE_GROUPS_OUTFILE = "google-groups.sh"
MAPPING_OUTFILE = "studies_to_google_access_groups.txt"

"""
Need a group all SAs will go in that will only have storage.objects.list iam permission on the bucket when using object-level ACL access.
This is because many Google APIs require both get and list permissions to act upon data in the bucket.
"""
ALL_SERVICE_ACCOUNTS_BUCKET_ID = "allProjects"

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.DEBUG)


def generate_cmd_sets(studies):
    """
    Generate command strings that can be executed in a Fence image
    to create google groups.
    Args:
        studies (array of strings): list of study_accession_with_consent strings to place in commands
    Returns:
        commands (array of strings): array of command strings
    """
    commands = []
    for study_accession_with_consent in studies:
        link_external_bucket_cmd = f"fence-create link-external-bucket --bucket-name {study_accession_with_consent}"
        commands.append(link_external_bucket_cmd)

    for study_accession_with_consent in studies:
        link_to_gen3_project_cmd = f"fence-create link-bucket-to-project --bucket_id {study_accession_with_consent} --bucket_provider google --project_auth_id {study_accession_with_consent}"
        commands.append(link_to_gen3_project_cmd)

    for study_accession_with_consent in studies:
        link_to_admin_cmd = f"fence-create link-bucket-to-project --bucket_id {study_accession_with_consent} --bucket_provider google --project_auth_id admin"
        commands.append(link_to_admin_cmd)

    for study_accession_with_consent in studies:
        link_all_projects_cmd = f"fence-create link-bucket-to-project --bucket_id {ALL_SERVICE_ACCOUNTS_BUCKET_ID} --bucket_provider google --project_auth_id {study_accession_with_consent}"
        commands.append(link_all_projects_cmd)

    return commands


def make_mapping_entries(study_accessions):
    """
    Generate list of google group names that can be placed in a studies_to_google_access_groups.txt file for use with manifestmerge script.
    Args:
        study_accessions (array of strings): list of study_accession_with_consent strings
    Returns:
        entries (array of strings): array of studies_to_google_access_groups.txt lines
    """
    entries = []
    for study in study_accessions:
        entries.append(
            "{}: stagedcp_{}_read_gbag@dcp.bionimbus.org".format(study, study)
        )
    return entries


def dedup_study_accessions(study_accessions):
    return sorted(list({thing.strip() for thing in study_accessions if "phs" in thing}))


def retrieve_study_accessions_from_extract(extract_filename):
    """Retrieve study_with_consent in a column-order-agnostic way"""
    with open(extract_filename) as f:
        on_header_line = True
        index_of_study_with_consent_field = -1
        undeduped_study_accessions = []
        for line in f:
            if on_header_line:
                field_names = line.split("\t")
                index_of_study_with_consent_field = field_names.index(
                    "study_with_consent"
                )
                if index_of_study_with_consent_field == -1:
                    raise ValueError("study_with_consent field not found in extract")
                on_header_line = False
            else:
                study_w_consent = line.split("\t")[index_of_study_with_consent_field]
                undeduped_study_accessions.append(study_w_consent)

        study_accessions = dedup_study_accessions(undeduped_study_accessions)
        return study_accessions


def write_list_of_strings_to_file_as_rows(array_in, output_filename):
    with open(output_filename, "a+") as out_file:
        out_file.write("\n".join(array_in))


def generate_google_group_cmds(dbgap_extract):
    study_accessions = retrieve_study_accessions_from_extract(dbgap_extract)

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


def main():
    parser = argparse.ArgumentParser(
        description="Generate set of fence-create commands for study-related Google Groups."
    )
    parser.add_argument("--dbgap_extract", help="a generated dbgap extract file")

    args = parser.parse_args(sys.argv[1:])

    if not args.dbgap_extract:
        logging.debug("-------")
        logging.debug("Usage error. Run this script using the below command form:")
        logging.debug(
            "> python generate_google_group_cmds.py --dbgap_extract <filename.tsv>"
        )
        logging.debug("-------")
        exit(0)

    generate_google_group_cmds(args.dbgap_extract)

if __name__ == "__main__":
    main()
