import csv
from collections import OrderedDict

def get_sample_data_from_manifest(manifest_file, dem="\t"):
    """
    get sample metadata from the genome manifest

    :param manifest_file: the path to the manifest
    :param dem: the delimiliter
    :return: a dictionary like this
            {
                "sample_id1": [{"aws_uri": "aws_uri_1", "gcp_uri": "gcp_uri_1", "md5": "md5_1", "file_size": "file_size_1"}, ...],
                ...
            }
    """

    files = OrderedDict()
    with open(manifest_file, "rt") as csvfile:
        csvReader = csv.DictReader(csvfile, delimiter=dem)
        for row in csvReader:
            row["file_size"] = int(row["file_size"])
            if row["sample_id"] in files:
                files[row["sample_id"]].append(row)
            else:
                files[row["sample_id"]] = [row]

    return files


def get_sample_info_from_dbgap_manifest(manifest_file, dem="\t"):
    """
    get sample info from dbgap manifest

    :param manifest_file: the path of the input manifest
    :param dem: 
    :return: a dictionary
    {
        "sample_id1": ["biosample_id": "biosample_id1", "sra_sample_id": "sra_sample_id1", ...],
        ...
    }
    """
    files = OrderedDict()
    with open(manifest_file, "rt") as csvfile:
        csvReader = csv.DictReader(csvfile, delimiter=dem)
        for row in csvReader:
            if row["submitted_sample_id"] in files:
                files[row["submitted_sample_id"]].append(row)
            else:
                files[row["submitted_sample_id"]] = [row]

    return files


def write_file(filename, rows, fieldnames=None):
    """

    :param filename:
    :param it:
    :param fieldnames:
    :return:
    """
    fieldnames = fieldnames or rows[0].keys()
    with open(filename, mode="w") as outfile:
        writer = csv.DictWriter(outfile, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def read_mapping_file(fname):
    """
    
    :param fname: path to the mapping file
    :return:
    """
    mapping = {}
    with open(fname, "r") as fopen:
        lines = fopen.readlines()
        for line in lines:
            words = line.split(":")
            mapping[words[0].strip()] = words[1].strip()

    return mapping
