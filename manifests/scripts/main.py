import os
import argparse
import scripts
import csv

import utils


def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="action", dest="action")

    merge_cmd = subparsers.add_parser("merge")
    merge_cmd.add_argument("--genome_manifest", required=True)
    merge_cmd.add_argument("--dbgap_manifest", required=True)
    merge_cmd.add_argument("--output", required=True)

    get_error_list_cmd = subparsers.add_parser("get_discrepancy_list")
    get_error_list_cmd.add_argument("--genome_manifest", required=True)
    get_error_list_cmd.add_argument("--dbgap_manifest", required=True)
    get_error_list_cmd.add_argument("--output", required=True)
    return parser.parse_args()


# python main.py merge --genome_manifest ../input/genome_file_manifest.csv --dbgap_manifest ../input/DataSTAGE_dbGaP_Consent_Extract.tsv --out ../output
def main():

    args = parse_arguments()

    genome_files = utils.get_sample_data_from_manifest(args.genome_manifest, dem=",")
    dbgap = utils.get_sample_info_from_dbgap_manifest(args.dbgap_manifest)

    if args.action == "merge":
        headers = [
            "sample_id",
            "dbgap_sample_id",
            "sra_sample_id",
            "biosample_id",
            "submitted_subject_id",
            "dbgap_subject_id",
            "consent_short_name",
            "study_accession_with_consent",
            "datastage_acl",
            "file_size",
            "md5",
            "aws_uri",
            "gcp_uri",
            "permission",
            "g_access_group",   
        ]
        results = scripts.merge_manifest(genome_files, dbgap)
        indexable_data = []
        for element in results:
            if element["g_access_group"]!="None":
                element["permission"] = "READ"
                indexable_data.append(element)

        utils.write_file(
            os.path.join(args.output, "DataSTAGE_indexable_data.tsv"), indexable_data, fieldnames=headers
        )

    if args.action == "get_discrepancy_list":
        headers = [
            "sample_use",
            "dbgap_status",
            "sra_data_details",
            "dbgap_subject_id",
            "repository",
            "submitted_sample_id",
            "study_accession_with_consent",
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
            os.path.join(args.output, "Data_not_part_of_DataSTAGE.tsv"), scripts.get_discrepancy_list(genome_files, dbgap), fieldnames=headers
        )
        headers = ["sample_id", "gcp_uri", "aws_uri", "file_size", "md5", "row_num"]
        utils.write_file(
            os.path.join(args.output, "DataSTAGE_data_requiring_additional_information.tsv"), scripts.get_discrepancy_list(dbgap, genome_files), fieldnames=headers
        )


if __name__ == "__main__":
    main()
