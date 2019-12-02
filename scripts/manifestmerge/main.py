import os
import sys
import argparse
import scripts
import csv
import utils

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

INDEXABLE_DATA_OUTPUT_FILENAME = "release_manifest.tsv"
MANUAL_REVIEW_OUTPUT_FILENAME = "data_requiring_manual_review.tsv"
EXTRANEOUS_DATA_OUTPUT_FILENAME = "extraneous_dbgap_metadata.tsv"
OUTPUT_FILES = (
    INDEXABLE_DATA_OUTPUT_FILENAME,
    MANUAL_REVIEW_OUTPUT_FILENAME,
    EXTRANEOUS_DATA_OUTPUT_FILENAME,
)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--genome_manifest", required=True)
    parser.add_argument("--dbgap_extract_file", required=True)
    parser.add_argument("--output", required=True)

    return parser.parse_args()


# python main.py --genome_manifest ../input/genome_file_manifest.csv --dbgap_extract_file ../input/DataSTAGE_dbGaP_Consent_Extract.tsv --out ../output
def main():
    args = parse_arguments()

    genome_files = utils.get_sample_data_from_manifest(args.genome_manifest, dem=",")
    dbgap = utils.get_sample_info_from_dbgap_extract_file(args.dbgap_extract_file)

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # Clear out output files
    for output_file in OUTPUT_FILES:
        if os.path.exists(output_file):
            os.remove(output_file)

    headers = [
        "GUID",
        "submitted_sample_id",
        "dbgap_sample_id",
        "sra_sample_id",
        "biosample_id",
        "submitted_subject_id",
        "dbgap_subject_id",
        "consent_short_name",
        "study_accession_with_consent",
        "study_accession",
        "study_with_consent",
        "datastage_subject_id",
        "consent_code",
        "sex",
        "body_site",
        "analyte_type",
        "sample_use",
        "repository",
        "dbgap_status",
        "sra_data_details",
        "file_size",
        "md5",
        "md5_hex",
        "aws_uri",
        "gcp_uri",
        "permission",
        "g_access_group",
    ]
    results = scripts.merge_manifest(genome_files, dbgap)
    indexable_data = []
    for element in results:
        if element["g_access_group"] != "None":
            element["permission"] = "READ"
            indexable_data.append(element)

    scripts.check_for_duplicates(indexable_data)

    utils.create_or_update_file_with_guid(
        os.path.join(args.output, INDEXABLE_DATA_OUTPUT_FILENAME),
        indexable_data,
        fieldnames=headers,
    )

    # get_discrepancy_list
    headers = [
        "sample_use",
        "dbgap_status",
        "sra_data_details",
        "dbgap_subject_id",
        "repository",
        "submitted_sample_id",
        "study_accession_with_consent",
        "study_accession",
        "study_with_consent",
        "datastage_subject_id",
        "consent_code",
        "sex",
        "body_site",
        "analyte_type",
        "sample_use",
        "repository",
        "dbgap_status",
        "sra_data_details",
        "submitted_subject_id",
        "consent_short_name",
        "analyte_type",
        "sra_sample_id",
        "sex",
        "biosample_id",
        "dbgap_sample_id",
        "consent_code",
        "study_accession",
        "body_site",
        "row_num",
    ]
    utils.write_file(
        os.path.join(args.output, EXTRANEOUS_DATA_OUTPUT_FILENAME),
        scripts.get_discrepancy_list(genome_files, dbgap),
        fieldnames=headers,
    )
    headers = [
        "submitted_sample_id",
        "gcp_uri",
        "aws_uri",
        "file_size",
        "md5",
        "row_num",
        "study_accession",
        "ignore",
    ]
    utils.write_file(
        os.path.join(args.output, MANUAL_REVIEW_OUTPUT_FILENAME),
        scripts.get_discrepancy_list(dbgap, genome_files),
        fieldnames=headers,
    )


if __name__ == "__main__":
    main()
