# Exit if any command fails
set -e
set -o pipefail

###############################################################################
# 1. Create a manifest from a bucket
export AWS_ACCESS_KEY_ID=$(jq -r .aws_creds.aws_access_key_id <<< $CREDS_JSON)
export AWS_SECRET_ACCESS_KEY=$(jq -r .aws_creds.aws_secret_access_key <<< $CREDS_JSON)
AWS_SESSION_TOKEN=$(jq -r .aws_creds.aws_session_token <<< $CREDS_JSON)
if [[ -z "$AWS_SESSION_TOKEN" ]]; then
  export AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN
fi
GS_CREDS_JSON=$(jq -r .gs_creds <<< $CREDS_JSON)
GCP_PROJECT_ID=$(jq -r .gcp_project_id <<< $CREDS_JSON)
GS_BUCKET_PATH=$(jq -r .gs_bucket_path <<< $CREDS_JSON)
AWS_BUCKET_PATH=$(jq -r .aws_bucket_path <<< $CREDS_JSON)
GITHUB_USER_EMAIL=$(jq -r .github_user_email <<< $CREDS_JSON)
GITHUB_PERSONAL_ACCESS_TOKEN=$(jq -r .github_personal_access_token <<< $CREDS_JSON)

cd scripts
echo $GS_CREDS_JSON >> gs_cloud_key.json
# gcloud auth activate-service-account --key-file=gs_cloud_key.json  --project=$GCP_PROJECT_ID

# GCP_PROJECT_ID=$GCP_PROJECT_ID ./generate-file-manifest.sh > ../genome_file_manifest.csv

###############################################################################
# 2. Create extract file
PHS_ID_LIST_PATH=/phs-id-list/`ls /phs-id-list/ | head -n 1`

cd /
git clone https://github.com/uc-cdis/dbgap-extract.git
cd dbgap-extract
# TODO: alter these 2 lines to use master branch
git checkout feat/validate-extract
git pull origin feat/validate-extract
pipenv install
pipenv run python3 dbgap_extract.py --study_accession_list_filename $PHS_ID_LIST_PATH --output_filename generated_extract.tsv

###############################################################################
# 3. Generate a list of commands to create Google Groups and a mapping file for the joindure script
cd /dataSTAGE-data-ingestion/scripts/
python3 generate_google_group_cmds.py --extract_filename /dbgap-extract/generated_extract.tsv
if [ -f "scripts/google-groups.sh" ]; then
  chmod +x scripts/google-groups.sh
fi
mv mapping.txt /dataSTAGE-data-ingestion/scripts/joindure/mapping.txt


###############################################################################
# 4. Run joindure script
cd /dataSTAGE-data-ingestion/scripts/joindure
mkdir output
pipenv run python3 main.py merge --genome_manifest /dataSTAGE-data-ingestion/genome_file_manifest.csv \
    --dbgap_manifest /dbgap-extract/generated_extract.tsv --out output

ls output


###############################################################################
# 5. Make PR to repo with outputs
cd /
git config --global user.email $GITHUB_USER_EMAIL
git clone "http://planxcyborg:$GITHUB_PERSONAL_ACCESS_TOKEN@github.com/uc-cdis/dataSTAGE-data-ingestion-private.git"

cd dataSTAGE-data-ingestion-private/
git pull origin master && git fetch --all
BRANCH_NAME_PREFIX='feat/release-'
RELEASE_NUMBER=$(python3 /dataSTAGE-data-ingestion/scripts/get_release_number.py --current_branches "$(git branch -a)")
echo "Creating branch $BRANCH_NAME_PREFIX$RELEASE_NUMBER"
git checkout -b "$BRANCH_NAME_PREFIX$RELEASE_NUMBER"
mkdir "release_$RELEASE_NUMBER"
cd "release_$RELEASE_NUMBER"
cp -R /dataSTAGE-data-ingestion/scripts/joindure/output/. .
mv ./release_manifest.tsv "./release_manifest_r$RELEASE_NUMBER.tsv"
cp /dbgap-extract/generated_extract.tsv "./generated_extract_r$RELEASE_NUMBER.tsv"
cp /dbgap-extract/generated_extract.log "./generated_extract_r$RELEASE_NUMBER.log"

git status
git commit -m "feat: release manifest"

# TODO: uncomment this line
# git push origin $BRANCH_NAME