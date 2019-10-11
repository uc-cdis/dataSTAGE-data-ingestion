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
    subparsers = parser.add_subparsers(title="action", dest="action")

    merge_cmd = subparsers.add_parser("merge")
    merge_cmd.add_argument("--genome_manifest", required=True)
    merge_cmd.add_argument("--dbgap_manifest", required=True)
    merge_cmd.add_argument("--output", required=True)

    return parser.parse_args()


# python main.py merge --genome_manifest ../input/genome_file_manifest.csv --dbgap_manifest ../input/DataSTAGE_dbGaP_Consent_Extract.tsv --out ../output
def main():

    args = parse_arguments()

    genome_files = utils.get_sample_data_from_manifest(args.genome_manifest, dem=",")
    dbgap = utils.get_sample_info_from_dbgap_manifest(args.dbgap_manifest)

    if args.action == "merge":
        headers = [
            "GUID",
            "sample_id",
            "dbgap_sample_id",
            "sra_sample_id",
            "biosample_id",
            "submitted_subject_id",
            "dbgap_subject_id",
            "consent_short_name",
            "study_accession_with_consent",
            "study_with_consent",
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

        utils.create_or_update_file_with_guid(
            os.path.join(args.output, "release_manifest.tsv"),
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
            "study_with_consent",
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
            os.path.join(args.output, "extraneous_dbgap_metadata.tsv"),
            scripts.get_discrepancy_list(genome_files, dbgap),
            fieldnames=headers,
        )
        headers = ["sample_id", "gcp_uri", "aws_uri", "file_size", "md5", "row_num"]
        utils.write_file(
            os.path.join(
                args.output, "Data_requiring_manual_review.tsv"
            ),
            scripts.get_discrepancy_list(dbgap, genome_files),
            fieldnames=headers,
        )


if __name__ == "__main__":
    main()
