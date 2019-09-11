import copy

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
    mapping = read_mapping_file("../config/mapping.txt")

    results = []

    for sample_id, metadata_collection in genome_files.iteritems():
        for meta_data in metadata_collection:
            if sample_id in dbgap:
                if len(dbgap[sample_id]) > 1:
                    print("WARNING: {} has more than one instance in dbgap".format(sample_id))
                for element in dbgap[sample_id]:
                    row = copy.deepcopy(meta_data)
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
                    row["datastage_acl"] = (
                        element.get("study_accession_with_consent") or "unreleased"
                    )
                    row["g_access_group"] = mapping.get(
                        element.get("study_accession_with_consent"), "None"
                    )
                    results.append(row)
            else:
                meta_data["biosample_id"] = "None"
                meta_data["dbgap_sample_id"] = "None"
                meta_data["sra_sample_id"] = "None"
                meta_data["submitted_subject_id"] = "None"
                meta_data["dbgap_subject_id"] = "None"
                meta_data["consent_short_name"] = "None"
                meta_data["study_accession_with_consent"] = "None"
                meta_data["datastage_acl"] = "unreleased"
                meta_data["g_access_group"] = "None"
                results.append(meta_data)

    return results


def get_discrepancy_list(genome_files, dbgap):
    results = []
    n = 1
    for sample_id, sample_info in dbgap.iteritems():
        if sample_id not in genome_files:
            for element in sample_info:
                element["row_num"] = n
                results.append(element)

                n = n + 1
        else:
            n = n + len(sample_info)

    return results
