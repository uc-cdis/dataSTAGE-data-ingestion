# This script is to be run from within a fence image

prune_commands_file () {
  EXISTING_GOOGLE_GROUPS_FILE=$1
  GOOGLE_GROUP_CREATE_SCRIPT_FILE=$2
  GOOGLE_GROUP_CREATE_SCRIPT_PRUNED_FILE=$3

  EXISTING_GROUPS=( )
  FOUND_GROUP_HEADER=0
  while IFS= read -r line || [ -n "$line" ]; do
    if [ $FOUND_GROUP_HEADER == 1 ]; then
      line_split=(${line//,/ })
      EXISTING_GROUPS+=("${line_split[2]}")
    fi

    if [ "$line" == 'GoogleBucketAccessGroup.email, Bucket.name, Project.auth_id' ]; then
      FOUND_GROUP_HEADER=1
    fi
  done < "$EXISTING_GOOGLE_GROUPS_FILE"

  NON_EXISTING_GROUPS=( )
  while IFS= read -r line || [ -n "$line" ]; do
    prune_this_group=0
    for i in "${EXISTING_GROUPS[@]}"; do
        if [[ $line == *"$i"* ]]; then
          prune_this_group=1
          echo "The group $i already exists. Skipping."
          break
        fi
    done
    if [ $prune_this_group == 0 ]; then
      NON_EXISTING_GROUPS+=("$line")
    fi
  done < "$GOOGLE_GROUP_CREATE_SCRIPT_FILE"

  printf "%s\n" "${NON_EXISTING_GROUPS[@]}" > $GOOGLE_GROUP_CREATE_SCRIPT_PRUNED_FILE

  echo "Pruned google groups commands:"
  cat $GOOGLE_GROUP_CREATE_SCRIPT_PRUNED_FILE
}

main () {
  echo 'Received output from data-ingestion-pipeline:'
  ls /data-ingestion-pipeline-output/

  fence-create google-list-authz-groups > "$EXISTING_GOOGLE_GROUPS_FILE"
  cat $EXISTING_GOOGLE_GROUPS_FILE

  existing_groups_file="google_list_authz_groups_output.txt"
  create_script_file="/data-ingestion-pipeline-output/google-groups.sh"
  pruned_commands_file_to_run="google-groups-pruned.sh"

  prune_commands_file $existing_groups_file $create_script_file $pruned_commands_file_to_run

  chmod +x $GOOGLE_GROUP_CREATE_SCRIPT_PRUNED_FILE
  if [ "$CREATE_GOOGLE_GROUPS" == "true" ]; then
    echo "Creating google groups..."
    ./$GOOGLE_GROUP_CREATE_SCRIPT_PRUNED_FILE
  fi
}

if [ "${1}" != "--source-only" ]; then
    main "${@}"
fi