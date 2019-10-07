import os
import sys
import copy
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from utils import (
    read_mapping_file,
    get_sample_data_from_manifest,
    get_sample_info_from_dbgap_manifest,
)


def merge_manifest(genome_files, dbgap):
    """
    merge two manifests
    
    :param genome_files: path to the genome manifest
    :param dbgap_file: path to the dbgap manifest
    :return:
    """
    mapping = read_mapping_file("mapping.txt")

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
                    row["study_with_consent"] = element.get(
                        "study_with_consent", "None"
                    )
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
                row["dbgap_sample_id"] = "None"
                row["sra_sample_id"] = "None"
                row["submitted_subject_id"] = "None"
                row["dbgap_subject_id"] = "None"
                row["consent_short_name"] = "None"
                row["study_with_consent"] = "None"
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
    results = []
    n = 1
    for sample_id, sample_info in dbgap.items():
        if sample_id not in genome_files:
            for element in sample_info:
                element["row_num"] = n
                results.append(element)

                n = n + 1
        else:
            n = n + len(sample_info)

    return results
