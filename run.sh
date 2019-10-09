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
export GS_CREDS_JSON=$(jq -r .gs_creds <<< $CREDS_JSON)
export GCP_PROJECT_ID=$(jq -r .gcp_project_id <<< $CREDS_JSON)
export GS_BUCKET_PATH=$(jq -r .gs_bucket_path <<< $CREDS_JSON)
export AWS_BUCKET_PATH=$(jq -r .aws_bucket_path <<< $CREDS_JSON)

aws s3 ls

cd scripts
echo $GS_CREDS_JSON >> gs_cloud_key.json
# gcloud auth activate-service-account --key-file=gs_cloud_key.json  --project=$GCP_PROJECT_ID

# GCP_PROJECT_ID=$GCP_PROJECT_ID ./generate-file-manifest.sh > ../genome_file_manifest.csv

###############################################################################
# 2. Create extract file
git clone https://github.com/uc-cdis/dbgap-extract.git
cd dbgap-extract
# TODO: alter these 2 lines to use master branch
git checkout feat/validate-extract
git pull origin feat/validate-extract
pipenv install
pipenv run python3 dbgap_extract.py --study_accession_list_filename ../test_phs_list.txt --output_filename generated_extract.tsv


###############################################################################
# 3. Generate a list of commands to create Google Groups and a mapping file for the joindure script
cd /dataSTAGE-data-ingestion/scripts/
python3 generate_google_group_cmds.py --extract_filename ../dbgap-extract/generated_extract.tsv
if [ -f "scripts/google-groups.sh" ]; then
  chmod +x scripts/google-groups.sh
fi
mv mapping.txt /dataSTAGE-data-ingestion/scripts/joindure/mapping.txt


###############################################################################
# 4. Run joindure script
cd /dataSTAGE-data-ingestion/scripts/joindure
mkdir output
pipenv run python3 main.py merge --genome_manifest /dataSTAGE-data-ingestion/genome_file_manifest.csv \
    --dbgap_manifest /dataSTAGE-data-ingestion/dbgap-extract/generated_extract.tsv --out output

ls output