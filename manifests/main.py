import settings

from utils import get_fileinfo_list_irc_manifest, get_fileinfo_list_dbgap_manifest, read_mapping_file, write_file


def main():

    mapping = read_mapping_file("./mapping.txt")
    
    genome_file = get_fileinfo_list_irc_manifest(settings.genome_file, dem=",")
    dbgap = get_fileinfo_list_dbgap_manifest(settings.DataSTAGE_dbGaP)
    import pdb; pdb.set_trace()
    for fi in genome_file:
        sample_id = fi.get("sample_id")
        fi["biosample_id"] = dbgap.get(sample_id, {}).get("biosample_id")
        fi["dbgap_sample_id"] = dbgap.get(sample_id, {}).get("dbgap_sample_id")
        fi["sra_sample_id"] = dbgap.get(sample_id, {}).get("sra_sample_id")
        fi["submitted_subject_id"] = dbgap.get(sample_id, {}).get("submitted_subject_id")
        fi["dbgap_subject_id"] = dbgap.get(sample_id, {}).get("dbgap_subject_id")
        fi["consent_short_name"] = dbgap.get(sample_id, {}).get("consent_short_name")
        fi["study_accession_with_consent"] = dbgap.get(sample_id, {}).get("study_accession_with_consent")
        fi["datastage_acl"] = dbgap.get(sample_id, {}).get("study_accession_with_consent") or "unreleased"
        fi["g_access_group"] = mapping.get(fi["datastage_acl"])
    
    headers = ["sample_id", "dbgap_sample_id", "sra_sample_id", "biosample_id", "submitted_subject_id", "dbgap_subject_id", "consent_short_name", "study_accession_with_consent", "datastage_acl", "file_size", "md5", "aws_uri", "gcp_uri", "g_access_group" ]
    write_file("./merged.tsv", genome_file, fieldnames=headers)


    print("end")


if __name__ == "__main__":
    main()