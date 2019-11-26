import os
import sys
import copy
import base64
from datetime import datetime
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from utils import (
    read_mapping_file,
    get_sample_data_from_manifest,
    get_sample_info_from_dbgap_extract_file,
)

LOG_FILE = "manifestmerge-log-" + datetime.now().strftime("%m-%d-%Y-%H-%M-%S") + ".log"
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def merge_manifest(genome_files, dbgap):
    """
    Merges data from two files -- the genome_file_manifest and the dbgap_extract -- 
    into one file against the sample_id column.
    
    Args:
        genome_files (string): path to the genome manifest
        dbgap_file (string): dbgap_file
    Returns:
        result (list of OrderedDicts): list of items with attributes from both sources
    """
    mapping = read_mapping_file("studys_to_google_access_groups.txt")

    results = []
    accession_missing_google_grp = set()

    for sample_id, metadata_collection in genome_files.items():
        for meta_data in metadata_collection:
            if sample_id in dbgap:
                if len(dbgap[sample_id]) > 1:
                    print(
                        "WARNING: {} has more than one instance in dbgap".format(
                            sample_id
                        )
                    )
                for element in dbgap[sample_id]:
                    row = copy.deepcopy(meta_data)
                    row["md5_hex"] = base64.b64decode(meta_data.get("md5")).hex()
                    row["biosample_id"] = element.get("biosample_id", "None")
                    row["submitted_sample_id"] = element.get(
                        "submitted_sample_id", "None"
                    )
                    row["dbgap_sample_id"] = element.get("dbgap_sample_id", "None")
                    row["sra_sample_id"] = element.get("sra_sample_id", "None")
                    row["submitted_subject_id"] = element.get(
                        "submitted_subject_id", "None"
                    )
                    row["dbgap_subject_id"] = element.get("dbgap_subject_id", "None")
                    row["consent_short_name"] = element.get(
                        "consent_short_name", "None"
                    )
                    row["study_accession_with_consent"] = element.get(
                        "study_accession_with_consent", "None"
                    )
                    row["study_accession"] = element.get("study_accession", "None")
                    row["study_with_consent"] = element.get(
                        "study_with_consent", "None"
                    )
                    row["datastage_subject_id"] = element.get(
                        "datastage_subject_id", "None"
                    )
                    row["consent_code"] = element.get("consent_code", "None")
                    row["sex"] = element.get("sex", "None")
                    row["body_site"] = element.get("body_site", "None")
                    row["analyte_type"] = element.get("analyte_type", "None")
                    row["sample_use"] = element.get("sample_use", "None")
                    row["repository"] = element.get("repository", "None")
                    row["dbgap_status"] = element.get("dbgap_status", "None")
                    row["sra_data_details"] = element.get("sra_data_details", "None")

                    accession_with_consent = element.get("study_with_consent")

                    if accession_with_consent is None:
                        print(
                            "ERROR: There is no accession with consent code for sample {}".format(
                                sample_id
                            )
                        )
                        row["g_access_group"] = "None"
                    else:
                        if accession_with_consent in mapping:
                            row["g_access_group"] = mapping[accession_with_consent]
                        else:
                            row["g_access_group"] = "None"
                            accession_missing_google_grp.add(accession_with_consent)

                    results.append(row)
            else:
                row = copy.deepcopy(meta_data)
                row["biosample_id"] = "None"
                row["submitted_sample_id"] = "None"
                row["dbgap_sample_id"] = "None"
                row["sra_sample_id"] = "None"
                row["submitted_subject_id"] = "None"
                row["dbgap_subject_id"] = "None"
                row["consent_short_name"] = "None"
                row["study_with_consent"] = "None"
                row["datastage_subject_id"] = "None"
                row["g_access_group"] = "None"
                row["md5_hex"] = "None"
                results.append(row)

    if accession_missing_google_grp:
        print(
            "ERROR: need to create google group for all study_with_consent in {}".format(
                sorted(list(accession_missing_google_grp))
            )
        )
        return []
    return results


def get_discrepancy_list(genome_files, dbgap):
    """
    Identifies sample_id's that are present in the second arg but not the first
    
    Args:
        genome_files (string): path to the genome manifest
        dbgap_file (string): dbgap_file
    Returns:
        results (list of OrderedDicts): list of items that are present in the second arg but not the first
    """
    results = []
    n = 1
    for sample_id, sample_info in dbgap.items():
        if sample_id not in genome_files:
            for element in sample_info:
                element["row_num"] = n
                element["study_accession"] = ""
                element["ignore"] = ""
                results.append(element)

                n = n + 1
        else:
            n = n + len(sample_info)

    return results


def get_unique_id(record):
    """ Returns unique id for a record in the format: '<sample_id><md5>' """
    return "sample-id: " + record["submitted_sample_id"] + ", md5: " + record["md5"]


def check_for_duplicates(indexable_data):
    """
    Throw a value error if there are duplicate records in the indexable_data output.
    The concatenation of the submitted_sample_id with the filename is to be unique
    Args:
        indexable_data (list of OrderedDicts): combined list of data items from merged manifests
    Returns:
        None
    """
    unique_ids = list(map(get_unique_id, indexable_data))

    # No duplicates
    if len(unique_ids) == len(set(unique_ids)):
        return

    # Find the duplicate
    duplicates = []
    id_dict = {}
    for uid in unique_ids:
        if uid not in id_dict:
            id_dict[uid] = 1
        else:
            duplicates.append(uid)
    error_message = "Error: Duplicate sample ids found in indexable data: {}.".format(
        str(duplicates)
    )
    logging.error(error_message)
    raise ValueError(error_message)
