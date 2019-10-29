# Run with:
# python3 -m pytest tests.py

import pytest
from mock import MagicMock
from mock import patch
import sys

sys.path.insert(0, "joindure")

import joindure.scripts as joindure
from test_data import *

###### Joindure tests #######
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

def test_check_for_duplicates():
    with pytest.raises(ValueError) as excinfo:
        L = joindure.check_for_duplicates(indexable_data_with_duplicates)
    assert "NWD2" in str(excinfo.value)
    assert "XJ4eRUTID0PBhEl4Vp4x/w==" in str(excinfo.value)

    # The test has passed if this does not throw an exception
    L = joindure.check_for_duplicates(indexable_data_with_no_duplicates)