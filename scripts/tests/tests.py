# Run all tests with:
# ./test_all.sh
# Run just this file with:
# pytest --cov=../../scripts --cov-config=../../.coveragerc tests.py

import sys

sys.path.insert(0, "manifestmerge")
sys.path.append("..")

import pytest
import os
from mock import MagicMock
from mock import patch
import manifestmerge
import get_release_number
import add_studies_from_manual_review
import generate_google_group_cmds
from test_data.test_data import *
from collections import OrderedDict

###### Test manifestmerge scripts #######
@patch("manifestmerge.scripts.read_mapping_file")
def test_merging(mock_read_mapping_file):
    """
    Basic test of manifest-merge functionality: 2 data pieces from disparate files
    are merged into one OrderedDict against the sample_id field
    """
    mock_read_mapping_file.return_value = {}
    L = manifestmerge.scripts.merge_manifest(genome_data, dbgap_data)
    assert len(L) == 4
    assert L[0]["sample_id"] == "sample_id1"
    assert L[0]["biosample_id"] == "biosample_id1"
    assert L[1]["sample_id"] == "sample_id1"
    assert L[1]["biosample_id"] == "biosample_id1_2"


@patch("manifestmerge.scripts.read_mapping_file")
def test_get_error_list(mock_read_mapping_file):
    """
    Tests case where the dbgap extract has one record not contained
    in the genome file manifest. We expect that this record will be placed
    in the extraneous-data file (produced by get_discrepancy_list()).
    """
    mock_read_mapping_file.return_value = {}
    L = manifestmerge.scripts.get_discrepancy_list(genome_data, dbgap_data)
    assert len(L) == 1
    assert L[0]["sample_id"] == "sample_id3"
    assert L[0]["biosample_id"] == "biosample_id3"
    assert L[0]["row_num"] == 4


def test_check_for_duplicates():
    """
    Tests case where the release manifest that is created contains
    two records with identical sample_ids and md5 hashes. Ensures the
    function check_for_duplicates() catches this.
    """
    with pytest.raises(ValueError) as excinfo:
        L = manifestmerge.scripts.check_for_duplicates(indexable_data_with_duplicates)
    assert "NWD2" in str(excinfo.value)
    assert "XJ4eRUTID0PBhEl4Vp4x/w==" in str(excinfo.value)

    # The test has passed if this does not throw an exception
    L = manifestmerge.scripts.check_for_duplicates(indexable_data_with_no_duplicates)


def test_sync_2_dicts():
    dict1 = { 'NWD1|abc' : { 'GUID': '860aec-007', 'submitted_sample_id': 'NWD1', 'md5': 'abc', 'file_size': 20 } }
    dict2 = { 'NWD2|def' : { 'GUID': '960aec-007', 'submitted_sample_id': 'NWD2', 'md5': 'def', 'file_size': 21 } }
    expected_output = {'NWD2|def': {'GUID': '960aec-007', 'submitted_sample_id': 'NWD2', 'md5': 'def', 'file_size': 21}, 'NWD1|abc': {'GUID': 'None', 'submitted_sample_id': 'NWD1', 'md5': 'abc', 'file_size': 20}}
    actual_output = manifestmerge.scripts.sync_2_dicts(dict1, dict2)
    assert len(actual_output.keys()) == len(expected_output.keys())
    assert len(actual_output.values()) == len(expected_output.values())
    assert all(
        [a == b for a, b in zip(actual_output.values(), expected_output.values())]
    )

    dict1 = { 'NWD1|abc' : { 'GUID': '860aec-007', 'submitted_sample_id': 'NWD1', 'md5': 'abc', 'file_size': 20 } }
    dict2 = { 'NWD1|abc' : { 'GUID': '860aec-007', 'submitted_sample_id': 'NWD1', 'md5': 'abc', 'file_size': 20 } }
    expected_output = dict1
    actual_output = manifestmerge.scripts.sync_2_dicts(dict1, dict2)
    assert len(actual_output.keys()) == len(expected_output.keys())
    assert len(actual_output.values()) == len(expected_output.values())
    assert all(
        [a == b for a, b in zip(actual_output.values(), expected_output.values())]
    )


def test_get_sample_data_from_manifest():
    expected_output = {}
    expected_output['NWD1'] = [ 
        OrderedDict([('submitted_sample_id', 'NWD1'),
                    (' aws_uri ', 's3://test-bucket/NWD1.b38.irc.v1.cram'),
                    ('gcp_uri ', 'gs://test-bucket-2/genomes/NWD1.b38.irc.v1.cram'),
                    ('file_size', '100'),
                    ('md5', 'fb23OXj8h9qX44uhlRei5A==')]),
        OrderedDict([('submitted_sample_id', 'NWD1'),
                    (' aws_uri ', 's3://test-bucket/NWD1.b38.irc.v1.vcf'),
                    ('gcp_uri ', 'gs://test-bucket-2/genomes/NWD1.b38.irc.v1.vcf'),
                    ('file_size', '200'),
                    ('md5', 'hb23OXj8h9qX44uhlRei6A==')])
    ]
    expected_output['NWD2'] = [
        OrderedDict([('submitted_sample_id', 'NWD2'),
            (' aws_uri ', 's3://test-bucket/NWD2.b38.irc.v1.cram'),
            ('gcp_uri ', 'gs://test-bucket-2/genomes/NWD2.b38.irc.v1.cram'),
            ('file_size', '100'),
            ('md5', 'ib23OXj8h9qX44uhlRei7A==')]),
        OrderedDict([('submitted_sample_id', 'NWD2'),
                (' aws_uri ', 's3://test-bucket/NWD2.b38.irc.v1.vcf'),
                ('gcp_uri ', 'gs://test-bucket-2/genomes/NWD2.b38.irc.v1.vcf'),
                ('file_size', '200'),
                ('md5', 'jb23OXj8h9qX44uhlRei8A==')])
    ]

    actual_output = manifestmerge.scripts.get_sample_data_from_manifest('test_data/test_genome_file_manifest.csv', dem=",")
    print(actual_output)
    assert expected_output == actual_output


def test_merge():
    actual_release_manifest_file = 'test_data/test_output/release_manifest.tsv'
    actual_data_requiring_manual_review_file = 'test_data/test_output/data_requiring_manual_review.tsv'
    actual_extraneous_data_file = 'test_data/test_output/extraneous_dbgap_metadata.tsv'
    
    if os.path.exists(actual_release_manifest_file):
        os.remove(actual_release_manifest_file)
    if os.path.exists(actual_data_requiring_manual_review_file):
        os.remove(actual_data_requiring_manual_review_file)
    if os.path.exists(actual_extraneous_data_file):
        os.remove(actual_extraneous_data_file)

    manifestmerge.scripts.merge(
        'test_data/test_genome_file_manifest.csv', 
        'test_data/test_extract.tsv', 
        'test_data/test_output/')
    
    with open(actual_release_manifest_file) as actual_release_manifest_output:
        pass
    with open(actual_data_requiring_manual_review_file) as actual_data_requiring_manual_review_output:
        pass
    with open(actual_extraneous_data_file) as actual_extraneous_data_output:
        pass

    assert 1 == 0


###### Test get_release_number.py #######
def test_get_release_number():
    """
    Tests case where the release manifest that is created contains
    two records with identical sample_ids and md5 hashes. Ensures the
    function check_for_duplicates() catches this.
    """
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

    git_branch_a_mock_output = """
      * master
        remotes/origin/HEAD -> origin/master
        remotes/origin/master
    """
    release_num = get_release_number.get_branch_number(git_branch_a_mock_output)
    assert release_num == 1


###### Test add_studies_from_manual_review.py #######
def test_retrieve_study_accessions_from_manual_review_file():
    """
    Unit test for the function retrieve_study_accessions_from_manual_review_file().
    Tests that study accessions are correctly retrieved from a test data_requiring_manual_review file.
    """
    actual_study_accessions = add_studies_from_manual_review.retrieve_study_accessions_from_manual_review_file(
        "test_data/test_data_requiring_manual_review.tsv"
    )

    expected_study_accessions = ["phs001143.v2", "phs1234", "phs909090"]
    assert all(
        [a == b for a, b in zip(actual_study_accessions, expected_study_accessions)]
    )


# ###### Test generate_google_group_cmds.py ######
def test_retrieve_from_study_accessions_from_extract():
    actual_study_accessions = generate_google_group_cmds.retrieve_study_accessions_from_extract(
        "test_data/test_extract.tsv"
    )

    expected_study_accessions = ['phs000920.c1', 'phs000921.c2']
    print(actual_study_accessions)
    assert all(
        [a == b for a, b in zip(actual_study_accessions, expected_study_accessions)]
    )


def test_dedup_study_accessions():
    """
    Unit test dedup_study_accessions function.
    """
    actual = generate_google_group_cmds.dedup_study_accessions(
        ["phs001143", "phs001145", "phs001148", "phs001148"]
    )
    expected = ["phs001143", "phs001145", "phs001148"]
    assert all([a == b for a, b in zip(actual, expected)])

    actual = generate_google_group_cmds.dedup_study_accessions(
        ["phs001143", "phs001145", "phs001148"]
    )
    expected = ["phs001143", "phs001145", "phs001148"]
    assert all([a == b for a, b in zip(actual, expected)])

    actual = generate_google_group_cmds.dedup_study_accessions(
        ["phs001143", "phs001143", "phs001143"]
    )
    expected = ["phs001143"]
    assert all([a == b for a, b in zip(actual, expected)])


def test_generate_cmd_sets():
    studies = ['phs001143.c1', 'phs003246', 'phs001143.c3']
    
    expected_cmd_sets = [
        'fence-create link-external-bucket --bucket-name phs001143.c1', 
        'fence-create link-external-bucket --bucket-name phs003246', 
        'fence-create link-external-bucket --bucket-name phs001143.c3', 
        'fence-create link-bucket-to-project --bucket_id phs001143.c1 --bucket_provider google --project_auth_id phs001143.c1', 
        'fence-create link-bucket-to-project --bucket_id phs003246 --bucket_provider google --project_auth_id phs003246', 
        'fence-create link-bucket-to-project --bucket_id phs001143.c3 --bucket_provider google --project_auth_id phs001143.c3', 
        'fence-create link-bucket-to-project --bucket_id phs001143.c1 --bucket_provider google --project_auth_id admin', 
        'fence-create link-bucket-to-project --bucket_id phs003246 --bucket_provider google --project_auth_id admin', 
        'fence-create link-bucket-to-project --bucket_id phs001143.c3 --bucket_provider google --project_auth_id admin', 
        'fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs001143.c1', 
        'fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs003246', 
        'fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs001143.c3'
    ]
    
    actual_cmd_sets = generate_google_group_cmds.generate_cmd_sets(studies)
    assert len(actual_cmd_sets) == 12
    assert all([a == b for a, b in zip(actual_cmd_sets, expected_cmd_sets)])

    studies = []
    expected_cmd_sets = []
    actual_cmd_sets = generate_google_group_cmds.generate_cmd_sets(studies)
    assert len(actual_cmd_sets) == 0
    assert all([a == b for a, b in zip(actual_cmd_sets, expected_cmd_sets)])

