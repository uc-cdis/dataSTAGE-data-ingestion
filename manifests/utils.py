import csv
from collections import OrderedDict

def get_fileinfo_list_irc_manifest(manifest_file, dem="\t"):
    """
    get file info from csv manifest
    """
    files = []
    with open(manifest_file, "rt") as csvfile:
        csvReader = csv.DictReader(csvfile, delimiter=dem)
        for row in csvReader:
            row["file_size"] = int(row["file_size"])
            files.append(row)

    return files

def get_fileinfo_list_dbgap_manifest(manifest_file, dem="\t"):
    """
    get file info from csv manifest
    """
    files = OrderedDict()
    with open(manifest_file, "rt") as csvfile:
        csvReader = csv.DictReader(csvfile, delimiter=dem)
        for row in csvReader:
            files[row["submitted_sample_id"]] = row

    return files


def write_file(filename, files, sorted_attr=None, fieldnames=None):
    def on_key(element):
        return element[sorted_attr]
    if sorted_attr:
        sorted_files = sorted(files, key=on_key)
    else:
        sorted_files = files

    if not files:
        return
    fieldnames = fieldnames or files[0].keys()
    import pdb; pdb.set_trace()
    with open(filename, mode="w") as outfile:
        writer = csv.DictWriter(outfile, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()

        for f in sorted_files:
            writer.writerow(f)

def read_mapping_file(fname):
    mapping = {}
    with open(fname, "r") as fopen:
        lines = fopen.readlines()
        for line in lines:
            words = line.split(":")
            mapping[words[0].strip()] = words[1].strip()

    return mapping
