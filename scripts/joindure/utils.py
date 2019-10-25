import os
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
            if row["submitted_sample_id"] in files:
                files[row["submitted_sample_id"]].append(row)
            else:
                files[row["submitted_sample_id"]] = [row]

    return files


def get_sample_info_from_dbgap_extract_file(manifest_file, dem="\t"):
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

    :param filename: the path to the file
    :param rows: a list of data rows
    :param fieldnames: a list of header
    :return: None
    """
    fieldnames = fieldnames or rows[0].keys()
    with open(filename, mode="w") as outfile:
        writer = csv.DictWriter(outfile, delimiter="\t", fieldnames=fieldnames, extrasaction='ignore')
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


def _sync_2_dicts(dict1, dict2):
    for key, new_row in dict1.items():
        if key not in dict2:
            new_row["GUID"] = "None"
            dict2[new_row["submitted_sample_id"] + "|" + new_row["md5"]] = new_row

    return dict2


def create_or_update_file_with_guid(fname, indexable_data, fieldnames=None):
    """
    if the file does not exit, create a file with indexable_data
    if the file does exis, merge the the file with indexable_data

    :param fname: output path
    :param indexable_data: a list of dictionary
    :param fieldnames: the file header
    :return: None
    """
    if not os.path.exists(fname):
        for data in indexable_data:
            data["GUID"] = "None"
        write_file(fname, indexable_data, fieldnames=fieldnames)
    else:
        dict1 = OrderedDict()
        dict2 = OrderedDict()

        for data in indexable_data:
            dict1[data["submitted_sample_id"] + "|" + data["md5"]] = data

        with open(fname, "rt") as csvfile:
            csvReader = csv.DictReader(csvfile, delimiter="\t")
            for row in csvReader:
                row["file_size"] = int(row["file_size"])
                dict2[row["submitted_sample_id"] + "|" + row["md5"]] = row

        # merge dict1 to dict1
        dict2 = _sync_2_dicts(dict1, dict2)
        L = [v for _, v in dict2.items()]
        write_file(fname, L, fieldnames)
