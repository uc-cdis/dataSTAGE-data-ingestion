import settings
import copy
import argparse
import scripts

from utils import get_fileinfo_list_irc_manifest, get_sample_info_from_dbgap_manifest, read_mapping_file, write_file



def parse_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="action", dest="action")

    merge_cmd = subparsers.add_parser("merge")
    merge_cmd.add_argument("--genome_manifest", required=True)
    merge_cmd.add_argument("--dbgap_manifest", required=True)
    merge_cmd.add_argument("--output", required=True)

    return parser.parse_args()

def main():

    args = parse_arguments()

    if args.action == "merge":
        scripts.merge_manifest(args.genome_file, args.dbgap_file, args.output)
        

        # # error list
        # result = []
        # N = 0
        # for sample_id, sample_info in dbgap.iteritems():
        #     if sample_id not in genome_file:
        #         #result = result + dbgap[sample_id]
        #         for element in sample_info:
        #             result.append(element)
        #         N = N + 1
        #         if N % 10000 == 0:
        #             print(N)
        
        # write_file("./error_list.tsv", result)

        # print("end")


if __name__ == "__main__":
    main()