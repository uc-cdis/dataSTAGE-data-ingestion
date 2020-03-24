# From within the tests folder, run all tests with:
# ./test_all.sh
# From within the tests folder, run just this file with:
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

###### Test manifestmerge #######
@patch("manifestmerge.scripts.read_mapping_file")
def test_merging(mock_read_mapping_file):
    """
    Basic test of manifest-merge functionality: 2 data pieces from disparate files
    are merged into one OrderedDict against the sample_id field
    """
    mock_read_mapping_file.return_value = {}
    L = manifestmerge.scripts.merge_manifest(genome_data, dbgap_data, 'studies_to_google_access_groups.txt')
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
        'studies_to_google_access_groups.txt',
        'test_data/test_output/')
    
    expected_release_manifest_output = ['GUID\tsubmitted_sample_id\tdbgap_sample_id\tsra_sample_id\tbiosample_id\tsubmitted_subject_id\tdbgap_subject_id\tconsent_short_name\tstudy_accession_with_consent\tstudy_accession\tstudy_with_consent\tdatastage_subject_id\tconsent_code\tsex\tbody_site\tanalyte_type\tsample_use\trepository\tdbgap_status\tsra_data_details\tfile_size\tmd5\tmd5_hex\taws_uri\tgcp_uri\tpermission\tg_access_group\n', 'None\tNWD1\t1234\t\tSAMN1234\tBUR01234\t12340\tDS-AB-CD-EF-1\tphs000920.v3.p2.c1\tphs000920.v3.p2\tphs000920.c1\tphs000920.v3_BUR01234\t1\tfemale\tPeripheral Blood\tDNA\t\tAB4321\tLoaded\t(location:Greenland|time:evening)\t100\tfb23OXj8h9qX44uhlRei5A==\t7dbdb73978fc87da97e38ba19517a2e4\ts3://test-bucket/NWD1.b38.irc.v1.cram\tgs://test-bucket-2/genomes/NWD1.b38.irc.v1.cram\tREAD\tstagedcp_phs000920.c1_read_gbag@dcp.bionimbus.org\n', 'None\tNWD1\t1234\t\tSAMN1234\tBUR01234\t12340\tDS-AB-CD-EF-1\tphs000920.v3.p2.c1\tphs000920.v3.p2\tphs000920.c1\tphs000920.v3_BUR01234\t1\tfemale\tPeripheral Blood\tDNA\t\tAB4321\tLoaded\t(location:Greenland|time:evening)\t200\thb23OXj8h9qX44uhlRei6A==\t85bdb73978fc87da97e38ba19517a2e8\ts3://test-bucket/NWD1.b38.irc.v1.vcf\tgs://test-bucket-2/genomes/NWD1.b38.irc.v1.vcf\tREAD\tstagedcp_phs000920.c1_read_gbag@dcp.bionimbus.org\n', 'None\tNWD2\t4321\t\tSAMN4321\tBUR04321\t43210\tDS-AB-CD-EF-2\tphs000921.v3.p2.c2\tphs000921.v3.p2\tphs000921.c2\tphs000921.v3_BUR04321\t2\tother\tEyes\tDNA\t\tAB1234\tLoaded\t(location:Eritrea|time:morning)\t100\tib23OXj8h9qX44uhlRei7A==\t89bdb73978fc87da97e38ba19517a2ec\ts3://test-bucket/NWD2.b38.irc.v1.cram\tgs://test-bucket-2/genomes/NWD2.b38.irc.v1.cram\tREAD\tstagedcp_phs000921.c2_read_gbag@dcp.bionimbus.org\n', 'None\tNWD2\t4321\t\tSAMN4321\tBUR04321\t43210\tDS-AB-CD-EF-2\tphs000921.v3.p2.c2\tphs000921.v3.p2\tphs000921.c2\tphs000921.v3_BUR04321\t2\tother\tEyes\tDNA\t\tAB1234\tLoaded\t(location:Eritrea|time:morning)\t200\tjb23OXj8h9qX44uhlRei8A==\t8dbdb73978fc87da97e38ba19517a2f0\ts3://test-bucket/NWD2.b38.irc.v1.vcf\tgs://test-bucket-2/genomes/NWD2.b38.irc.v1.vcf\tREAD\tstagedcp_phs000921.c2_read_gbag@dcp.bionimbus.org\n']
    expected_data_requiring_manual_review_output = ['submitted_sample_id\tgcp_uri\taws_uri\tfile_size\tmd5\trow_num\tstudy_accession\tignore\n']
    expected_extraneous_data_output = ['sample_use\tdbgap_status\tsra_data_details\tdbgap_subject_id\trepository\tsubmitted_sample_id\tstudy_accession_with_consent\tstudy_accession\tstudy_with_consent\tdatastage_subject_id\tconsent_code\tsex\tbody_site\tanalyte_type\tsample_use\trepository\tdbgap_status\tsra_data_details\tsubmitted_subject_id\tconsent_short_name\tanalyte_type\tsra_sample_id\tsex\tbiosample_id\tdbgap_sample_id\tconsent_code\tstudy_accession\tbody_site\trow_num\n', '\tLoaded\t(location:Zaire|time:afternoon\t0\tAB0000\tNWD3\tphs000921.v3.p2.c2\t\tphs000921.c2\tphs000921.v3_BUR00000\t3\tnot specified\tMouth\tRNA\t\tAB0000\tLoaded\t(location:Zaire|time:afternoon\tBUR00000\tDS-AB-CD-EF-3\tRNA\t\tnot specified\tSAMN0000\t0\t3\t\tMouth\t3\n']

    with open(actual_release_manifest_file) as actual_release_manifest_output:
        r = actual_release_manifest_output.readlines()
        print('\n\nayeeeee\n\n\n')
        print(expected_release_manifest_output)
        print('-----')
        print(r)
        assert expected_release_manifest_output == r
    with open(actual_data_requiring_manual_review_file) as actual_data_requiring_manual_review_output:
        r = actual_data_requiring_manual_review_output.readlines()
        assert expected_data_requiring_manual_review_output == r
    with open(actual_extraneous_data_file) as actual_extraneous_data_output:
        r = actual_extraneous_data_output.readlines()
        assert expected_extraneous_data_output == r


###### Test utils.py #######
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
    expected_output = OrderedDict()
    expected_output['NWD1'] = [ 
        OrderedDict([('submitted_sample_id', 'NWD1'),
                    ('aws_uri', 's3://test-bucket/NWD1.b38.irc.v1.cram'),
                    ('gcp_uri', 'gs://test-bucket-2/genomes/NWD1.b38.irc.v1.cram'),
                    ('file_size', 100),
                    ('md5', 'fb23OXj8h9qX44uhlRei5A==')]),
        OrderedDict([('submitted_sample_id', 'NWD1'),
                    ('aws_uri', 's3://test-bucket/NWD1.b38.irc.v1.vcf'),
                    ('gcp_uri', 'gs://test-bucket-2/genomes/NWD1.b38.irc.v1.vcf'),
                    ('file_size', 200),
                    ('md5', 'hb23OXj8h9qX44uhlRei6A==')])
    ]
    expected_output['NWD2'] = [
        OrderedDict([('submitted_sample_id', 'NWD2'),
            ('aws_uri', 's3://test-bucket/NWD2.b38.irc.v1.cram'),
            ('gcp_uri', 'gs://test-bucket-2/genomes/NWD2.b38.irc.v1.cram'),
            ('file_size', 100),
            ('md5', 'ib23OXj8h9qX44uhlRei7A==')]),
        OrderedDict([('submitted_sample_id', 'NWD2'),
                ('aws_uri', 's3://test-bucket/NWD2.b38.irc.v1.vcf'),
                ('gcp_uri', 'gs://test-bucket-2/genomes/NWD2.b38.irc.v1.vcf'),
                ('file_size', 200),
                ('md5', 'jb23OXj8h9qX44uhlRei8A==')])
    ]

    actual_output = manifestmerge.scripts.get_sample_data_from_manifest('test_data/test_genome_file_manifest.csv', dem=",")
    assert expected_output == actual_output


###### Test get_release_number.py #######
def test_get_branch_number():
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


def test_retrieve_study_accessions_from_phs_id_list_file():
    actual_study_accessions = add_studies_from_manual_review.retrieve_study_accessions_from_phs_id_list_file(
        "test_data/phs_ids.txt"
    )

    expected_study_accessions = ["phs000920.v3.p2.c1", "phs000921.v3.p2.c2"]
    assert all(
        [a == b for a, b in zip(actual_study_accessions, expected_study_accessions)]
    )


def test_add_studies_from_manual_review():
    add_studies_from_manual_review.add_studies_from_manual_review(
        'test_data/phs_ids.txt', 
        'test_data/test_data_requiring_manual_review.tsv', 
        'test_data/requiring_manual_review_output.txt'
    )

    with open('test_data/requiring_manual_review_output.txt') as f:
        actual_output = f.readlines()
        expected_output = ['phs001143.v2\n', 'phs1234\n', 'phs909090\n', 'phs000920.v3.p2.c1\n', 'phs000921.v3.p2.c2']

        assert expected_output == actual_output

####### Test generate_google_group_cmds.py ######
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


def test_make_mapping_entries():
    study_accessions = ['phs00920', 'phs00921.v3', 'phs119992002.c3.p5.c64']
    
    expected_make_mapping_entries = [
        'phs00920: stagedcp_phs00920_read_gbag@dcp.bionimbus.org', 
        'phs00921.v3: stagedcp_phs00921.v3_read_gbag@dcp.bionimbus.org', 
        'phs119992002.c3.p5.c64: stagedcp_phs119992002.c3.p5.c64_read_gbag@dcp.bionimbus.org'
    ]
    actual_make_mapping_entries =  generate_google_group_cmds.make_mapping_entries(study_accessions)

    assert expected_make_mapping_entries == actual_make_mapping_entries


def test_generate_generate_google_group_cmds():
    generate_google_group_cmds.generate_google_group_cmds('test_data/test_extract.tsv')
    with open('google-groups.sh') as f:
        actual_output = f.readlines()
        expected_output = ['fence-create link-external-bucket --bucket-name phs000920.c1\n', 'fence-create link-external-bucket --bucket-name phs000921.c2\n', 'fence-create link-bucket-to-project --bucket_id phs000920.c1 --bucket_provider google --project_auth_id phs000920.c1\n', 'fence-create link-bucket-to-project --bucket_id phs000921.c2 --bucket_provider google --project_auth_id phs000921.c2\n', 'fence-create link-bucket-to-project --bucket_id phs000920.c1 --bucket_provider google --project_auth_id admin\n', 'fence-create link-bucket-to-project --bucket_id phs000921.c2 --bucket_provider google --project_auth_id admin\n', 'fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs000920.c1\n', 'fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs000921.c2']
        assert actual_output == expected_output
    
    with open('studies_to_google_access_groups.txt') as f:
        actual_output = f.readlines()
        expected_output = ['phs000920.c1: stagedcp_phs000920.c1_read_gbag@dcp.bionimbus.org\n', 'phs000921.c2: stagedcp_phs000921.c2_read_gbag@dcp.bionimbus.org']
        assert actual_output == expected_output