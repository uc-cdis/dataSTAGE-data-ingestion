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
    echo "--**--"
    echo "$expected"
    echo "--**--"
    assert_equal "$actual" "$expected"
}
