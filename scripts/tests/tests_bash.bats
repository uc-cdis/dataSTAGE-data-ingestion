#!../libs/bats/bin/bats

# This is a test script written in Bash Automated Test System ("bats")
# https://github.com/sstephenson/bats

load '../libs/bats-support/load'
load '../libs/bats-assert/load'

source fence-image-commands.sh --source-only

@test "fence-image-commands.sh should use google-list-authz-results to correctly prune creation commands" {
    existing_groups_file="tests/test_data/google_list_authz_groups_output.txt"
    create_script_file="tests/test_data/google-groups.sh"
    pruned_commands_file_to_run="tests/test_data/google-groups-pruned.sh"

    # 2 existing google groups
    cat > "$existing_groups_file" << EOF
GoogleBucketAccessGroup.email, Bucket.name, Project.auth_id
cde@example.com, s3://bucket-name, phs4321
EOF

    # 1 of these existing groups is in the data-ingestion-pipeline output
    cat > "$create_script_file" << EOF
fence-create link-external-bucket --bucket-name phs1234
fence-create link-external-bucket --bucket-name phs4321
fence-create link-bucket-to-project --bucket_id phs1234 --bucket_provider google --project_auth_id phs1234
fence-create link-bucket-to-project --bucket_id phs4321 --bucket_provider google --project_auth_id phs4321
fence-create link-bucket-to-project --bucket_id phs1234 --bucket_provider google --project_auth_id topmed
fence-create link-bucket-to-project --bucket_id phs4321 --bucket_provider google --project_auth_id topmed
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs1234
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs4321
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs1234
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs4321
EOF

	prune_commands_file $existing_groups_file $create_script_file $pruned_commands_file_to_run
    
    actual=`cat $pruned_commands_file_to_run`
    expected=$(cat <<-END
fence-create link-external-bucket --bucket-name phs1234
fence-create link-bucket-to-project --bucket_id phs1234 --bucket_provider google --project_auth_id phs1234
fence-create link-bucket-to-project --bucket_id phs1234 --bucket_provider google --project_auth_id topmed
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs1234
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs1234
END
)
    assert_equal "$actual" "$expected"
}

@test "unit test phs_from_fence_cmds function" { 
    file_to_retrieve_phs_from="tests/test_data/google-groups.sh"
    file_to_output_results_to="tests/test_data/phs_output.txt"
    if [ -f "$file_to_retrieve_phs_from" ]; then
        rm "$file_to_retrieve_phs_from"
    fi
    if [ -f "$file_to_output_results_to" ]; then
        rm "$file_to_output_results_to"
    fi

    # 1 of these existing groups is in the data-ingestion-pipeline output
    cat > "$file_to_retrieve_phs_from" << EOF
fence-create link-external-bucket --bucket-name phs1234
fence-create link-external-bucket --bucket-name phs4321
fence-create link-bucket-to-project --bucket_id phs1234 --bucket_provider google --project_auth_id phs1234
fence-create link-bucket-to-project --bucket_id phs4321 --bucket_provider google --project_auth_id phs4321
fence-create link-bucket-to-project --bucket_id phs1234 --bucket_provider google --project_auth_id topmed
fence-create link-bucket-to-project --bucket_id phs4321 --bucket_provider google --project_auth_id topmed
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs1234
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs4321
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs1234
fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id phs4321
EOF

    phs_from_file $file_to_retrieve_phs_from $file_to_output_results_to
    
    actual=`cat $file_to_output_results_to`
    expected=$(cat <<-END
phs1234 phs4321
END
)
    assert_equal "$actual" "$expected"
}

@test "joindure script and generate_google_group_cmds.py work together locally as expected" {   
    if [ -f "studys_to_google_access_groups.txt" ]; then
        rm studys_to_google_access_groups.txt
    fi

    python3 generate_google_group_cmds.py --extract_filename tests/test_data/test_extract.tsv

    assert [ -f "studys_to_google_access_groups.txt" ]
    actual_mapping=`cat studys_to_google_access_groups.txt`
    expected_mapping=`cat tests/test_data/expected_output/studys_to_google_access_groups.txt`
    assert_equal "$actual_mapping" "$expected_mapping"

    assert [ -f "google-groups.sh" ]
    actual_google_groups=`cat google-groups.sh`
    expected_google_groups=`cat tests/test_data/expected_output/google-groups.sh`
    assert_equal "$actual_google_groups" "$expected_google_groups"

    mv studys_to_google_access_groups.txt joindure/

    cd joindure/

    pipenv run python3 main.py merge --genome_manifest ../tests/test_data/test_genome_file_manifest.csv \
    --dbgap_extract_file ../tests/test_data/test_extract.tsv --out ../tests/test_data/output

    ls output
    
    # Should create 3 files
    number_of_files_created=`ls -1q output/ | wc -l`
    assert_equal $number_of_files_created 3

    assert [ -f "output/release_manifest.tsv" ]
    assert [ -f "output/extraneous_dbgap_metadata.tsv" ]
    assert [ -f "output/data_requiring_manual_review.tsv" ]

    actual_release_manifest=`cat ../tests/test_data/output/release_manifest.tsv`
    expected_release_manifest=`cat ../tests/test_data/expected_output/release_manifest.tsv`
    assert_equal "$actual_release_manifest" "$expected_release_manifest"
    
    actual_extraneous_data=`cat ../tests/test_data/output/extraneous_dbgap_metadata.tsv`
    expected_extraneous_data=`cat ../tests/test_data/expected_output/extraneous_dbgap_metadata.tsv`
    assert_equal "$actual_extraneous_data" "$expected_extraneous_data"

    actual_data_requiring_manual_review=`cat ../tests/test_data/output/data_requiring_manual_review.tsv`
    expected_data_requiring_manual_review=`cat ../tests/test_data/expected_output/data_requiring_manual_review.tsv`
    assert_equal "$actual_data_requiring_manual_review" "$expected_data_requiring_manual_review"

    rm ../tests/joindure-log*.log
}