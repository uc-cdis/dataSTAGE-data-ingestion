from collections import OrderedDict

def convert_to_list_of_ordered_dicts(list_of_dicts):
    if len(list_of_dicts) == 0:
        return []
    keys = list(list_of_dicts[0].keys()) # arbitrary key order
    list_of_ordered_dicts = []
    for element in list_of_dicts:
        ordered_dict = OrderedDict()
        for key in keys:
            ordered_dict[key] = element[key]
        list_of_ordered_dicts.append(ordered_dict)

    return list_of_ordered_dicts

genome_data = {
    "sample_id1": [
        {
            "sample_id": "sample_id1",
            "aws_uri": "aws_uri_1",
            "gcp_uri": "gcp_uri_1",
            "md5": "md5_1",
            "file_size": "file_size_1",
        }
    ],
    "sample_id2": [
        {
            "sample_id": "sample_id2",
            "aws_uri": "aws_uri_2",
            "gcp_uri": "gcp_uri_2",
            "md5": "md5_2",
            "file_size": "file_size_2",
        },
        {
            "aws_uri": "aws_uri_2",
            "gcp_uri": "gcp_uri_2",
            "md5": "md5_2",
            "file_size": "file_size_2",
        },
    ],
}

dbgap_data = {
    "sample_id1": [
        {
            "sample_id": "sample_id1",
            "biosample_id": "biosample_id1",
            "sra_sample_id": "sra_sample_id1",
        },
        {
            "sample_id": "sample_id2",
            "biosample_id": "biosample_id1_2",
            "sra_sample_id": "sra_sample_id1_2",
        },
    ],
    "sample_id2": [
        {
            "sample_id": "sample_id2",
            "biosample_id": "biosample_id2",
            "sra_sample_id": "sra_sample_id2",
        }
    ],
    "sample_id3": [
        {
            "sample_id": "sample_id3",
            "biosample_id": "biosample_id3",
            "sra_sample_id": "sra_sample_id3",
        }
    ],
}

# Duplicate submitted_sample_ids with matching md5 hashes, so this is invalid data
indexable_data_with_duplicates = [
    {
        'submitted_sample_id': 'NWD1',
        'submitted_subject_id': 'Gene_1234a',
        'aws_uri': 's3://bucket/file.csi',
        'gcp_uri': 'gs://bucket/file.csi',
        'md5': 'XJ4eRUTID0PBhEl4Vp4x/w==',
        'md5_hex': '5c9e1e4544c80f43c1844978569e31ff'
    },
    {
        'submitted_sample_id': 'NWD2',
        'submitted_subject_id': 'Gene_1234b',
        'aws_uri': 's3://bucket/file.csi',
        'gcp_uri': 'gs://bucket/file.csi',
        'md5': 'XJ4eRUTID0PBhEl4Vp4x/w==',
        'md5_hex': '5c9e1e4544c80f43c1844978569e31ff'
    },
    {
        'submitted_sample_id': 'NWD2',
        'submitted_subject_id': 'Gene_1234c',
        'aws_uri': 's3://bucket/file.csi',
        'gcp_uri': 'gs://bucket/file.csi',
        'md5': 'XJ4eRUTID0PBhEl4Vp4x/w==',
        'md5_hex': '5c9e1e4544c80f43c1844978569e31ff'
    }
]
indexable_data_with_duplicates = convert_to_list_of_ordered_dicts(indexable_data_with_duplicates)

# Duplicate submitted_sample_ids, but the md5 hashes for these are unique, so this is valid data
indexable_data_with_no_duplicates = [
    {
        'submitted_sample_id': 'NWD1',
        'submitted_subject_id': 'Gene_1234a',
        'aws_uri': 's3://bucket/file.csi',
        'gcp_uri': 'gs://bucket/file.csi',
        'md5': 'XJ4eRUTID0PBhEl4Vp4x/w==',
        'md5_hex': '5c9e1e4544c80f43c1844978569e31ff'
    },
    {
        'submitted_sample_id': 'NWD2',
        'submitted_subject_id': 'Gene_1234b',
        'aws_uri': 's3://bucket/file.csi',
        'gcp_uri': 'gs://bucket/file.csi',
        'md5': 'XJ4eRUTID0PBhEl4Vp4x/w==',
        'md5_hex': '5c9e1e4544c80f43c1844978569e31ff'
    },
    {
        'submitted_sample_id': 'NWD2',
        'submitted_subject_id': 'Gene_1234c',
        'aws_uri': 's3://bucket/file.csi',
        'gcp_uri': 'gs://bucket/file.csi',
        'md5': 'XJ4eRUTID0PBhEl4Vp4x/z==',
        'md5_hex': '5c9e1e4544c80f43c1944978569e31ff'
    }
]

indexable_data_with_no_duplicates = convert_to_list_of_ordered_dicts(indexable_data_with_no_duplicates)