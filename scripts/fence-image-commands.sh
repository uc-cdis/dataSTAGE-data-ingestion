# This script is to be run from within a fence image

while true; do
    files=( /data-ingestion-pipeline-output/* )
    (( ${#files[@]} >= 3 )) && break
    sleep 5s
done

echo 'Received output from data-ingestion-pipeline:'
ls /data-ingestion-pipeline-output/

EXISTING_GOOGLE_GROUPS_FILE="google_list_authz_groups_output.txt"
GOOGLE_GROUP_CREATE_SCRIPT_FILE="/data-ingestion-pipeline-output/google-groups.sh"
GOOGLE_GROUP_CREATE_SCRIPT_PRUNED_FILE="google-groups-pruned.sh"

fence-create google-list-authz-groups > $EXISTING_GOOGLE_GROUPS_FILE

EXISTING_GROUPS=( )
FOUND_GROUP_HEADER=0
while IFS= read -r line || [ -n "$line" ]; do
  if [ $FOUND_GROUP_HEADER == 1 ]; then
    line_split=(${line//,/ })
    EXISTING_GROUPS+=("${line_split[1]}")
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

chmod +x $GOOGLE_GROUP_CREATE_SCRIPT_PRUNED_FILE
while getopts ":a:" opt; do
  case $opt in
    create_google_groups)
      if [ $OPTARG == 'true' ]; then
        # ./$GOOGLE_GROUP_CREATE_SCRIPT_PRUNED_FILE
        echo 'would have run the command'
      fi
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done