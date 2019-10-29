# Run with:
# python3 -m pytest tests.py

import sys

sys.path.insert(0, "joindure")

import pytest
from mock import MagicMock
from mock import patch
import joindure.scripts as joindure
import get_release_number
import add_studies_from_manual_review
import generate_google_group_cmds
from test_data.test_data import *


###### Test joindure script #######
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


###### Test get_release_number.py #######
def test_get_release_number():
    git_branch_a_mock_output = """
        * feat/release-703\nmaster\nremotes/origin/HEAD -> origin/master
        remotes/origin/feat/release-703
        remotes/origin/feat/release-702
        remotes/origin/master
        remotes/origin/feat/bug-fixes
    """
    release_num = get_release_number.get_branch_number(git_branch_a_mock_output)
    assert release_num == 704

    git_branch_a_mock_output = """
        feat/release-1
      * master
        remotes/origin/HEAD -> origin/master
        remotes/origin/feat/release-1
        remotes/origin/master
    """
    release_num = get_release_number.get_branch_number(git_branch_a_mock_output)
    assert release_num == 2


###### Test add_studies_from_manual_review.py #######
def test_retrieve_study_accessions_from_manual_review_file():
    actual_study_accessions = add_studies_from_manual_review.retrieve_study_accessions_from_manual_review_file(
        "test_data/test_data_requiring_manual_review.tsv"
    )

    expected_study_accessions = ["phs001143.v2", "phs1234", "phs909090"]
    assert all(
        [a == b for a, b in zip(actual_study_accessions, expected_study_accessions)]
    )


###### Test generate_google_group_cmds.py ######
def test_dedup_study_accessions():
    actual = generate_google_group_cmds.dedup_study_accessions(
        ["phs001143", "phs001145", "phs001148", "phs001148"]
    )
    expected = ["phs001143", "phs001145", "phs001148"]
    assert all(
        [a == b for a, b in zip(actual, expected)]
    )