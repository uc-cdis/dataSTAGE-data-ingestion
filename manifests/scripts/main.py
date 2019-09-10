import settings
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

    get_error_list_cmd = subparsers.add_parser("get_error_list")
    get_error_list_cmd.add_argument("--genome_manifest", required=True)
    get_error_list_cmd.add_argument("--dbgap_manifest", required=True)
    get_error_list_cmd.add_argument("--output", required=True)
    return parser.parse_args()


#python main.py merge --genome_manifest ../input/genome_files_manifest.csv --dbgap_manifest ../input/DataSTAGE_dbGaP_Consent_Extract.tsv --out ../output/merged.tsv
def main():

    args = parse_arguments()

    genome_files = utils.get_sample_data_from_manifest(args.genome_manifest, dem=",")
    dbgap = utils.get_sample_info_from_dbgap_manifest(args.dbgap_manifest)

    if args.action == "merge":
        headers = ["sample_id", "dbgap_sample_id", "sra_sample_id", "biosample_id", "submitted_subject_id", "dbgap_subject_id", "consent_short_name", "study_accession_with_consent", "datastage_acl", "file_size", "md5", "aws_uri", "gcp_uri", "g_access_group" ]
        utils.write_file(args.output, scripts.merge_manifest(genome_files, dbgap), fieldnames=headers)
    
    if args.action == "get_error_list":
        utils.write_file(args.output, scripts.get_error_list(genome_files, dbgap))


if __name__ == "__main__":
    main()