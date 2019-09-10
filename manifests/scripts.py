from utils import (
    get_sample_data_from_manifest,
    get_sample_info_from_dbgap_manifest
)


def merge_manifest(genome_file, dbgap_file):
    mapping = read_mapping_file("./mapping.txt")
    genome_file = get_sample_data_from_manifest(genome_file, dem=",")
    dbgap = get_sample_info_from_dbgap_manifest(dbgap_file)

    result = []
    for sample_id, metadata_collection in genome_file.iteritems():
        
        for meta_data in metadata_collection:
            if sample_id in dbgap:
                for element in dbgap[sample_id]:
                    row = copy.deepcopy(meta_data)
                    row["biosample_id"] = element.get("biosample_id", "None")
                    row["dbgap_sample_id"] = element.get("dbgap_sample_id", "None")
                    row["sra_sample_id"] = element.get("sra_sample_id", "None")
                    row["submitted_subject_id"] = element.get("submitted_subject_id", "None")
                    row["dbgap_subject_id"] = element.get("dbgap_subject_id", "None")
                    row["consent_short_name"] = element.get("consent_short_name", "None")
                    row["study_accession_with_consent"] = element.get("study_accession_with_consent", "None")
                    row["datastage_acl"] = element.get("study_accession_with_consent") or "unreleased"
                    row["g_access_group"] = mapping.get(element.get("study_accession_with_consent"), "None")
                    #result.append(row)
                    yield row
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
                #result.append(meta_data)
                yield row

    #return result
    # headers = ["sample_id", "dbgap_sample_id", "sra_sample_id", "biosample_id", "submitted_subject_id", "dbgap_subject_id", "consent_short_name", "study_accession_with_consent", "datastage_acl", "file_size", "md5", "aws_uri", "gcp_uri", "g_access_group" ]
    # write_file("./merged.tsv", result, fieldnames=headers)