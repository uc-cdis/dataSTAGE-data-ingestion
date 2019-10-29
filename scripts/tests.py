# Run with:
# python3 -m pytest tests.py

import pytest
from mock import MagicMock
from mock import patch
import sys

sys.path.insert(0, "joindure")

import joindure.scripts as joindure


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


@patch("joindure.scripts.read_mapping_file")
def test_merging(mock_read_mapping_file):
    mock_read_mapping_file.return_value = {}
    L = joindure.merge_manifest(genome_data, dbgap_data)
    assert len(L) == 4
    assert L[0]["sample_id"] == "sample_id1"
    assert L[0]["biosample_id"] == "biosample_id1"
    assert L[1]["sample_id"] == "sample_id1"
    assert L[1]["biosample_id"] == "biosample_id1_2"


@patch("joindure.scripts.read_mapping_file")
def test_get_error_list(mock_read_mapping_file):
    mock_read_mapping_file.return_value = {}
    L = joindure.get_discrepancy_list(genome_data, dbgap_data)
    assert len(L) == 1
    assert L[0]["sample_id"] == "sample_id3"
    assert L[0]["biosample_id"] == "biosample_id3"
    assert L[0]["row_num"] == 4
