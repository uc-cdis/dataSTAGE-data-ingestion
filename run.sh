# Exit if any command fails
set -e
set -o pipefail

###############################################################################
# 1. (Optional) Check for additional PHS ID inputs that should be included from the review process
PHS_ID_LIST_PATH=/phs-id-list/`ls /phs-id-list/ | head -n 1`
DATA_FROM_MANUAL_REVIEW='/dataSTAGE-data-ingestion/data_requiring_manual_review.tsv'

if [ -d "/data-from-manual-review/" ]; then
	files_in_manual_review_mount=( /data-from-manual-review/* )
	if [ ${#files_in_manual_review_mount[@]} -ge 1 ]; then
		DATA_FROM_MANUAL_REVIEW=/data-from-manual-review/`ls /data-from-manual-review/ | head -n 1`
		cd /dataSTAGE-data-ingestion/scripts/
		python3 add_studies_from_manual_review.py --phs_id_list $PHS_ID_LIST_PATH \
			--data_requiring_manual_review $DATA_FROM_MANUAL_REVIEW \
			--output_file merged_phs_id_list.txt
		PHS_ID_LIST_PATH=/dataSTAGE-data-ingestion/scripts/merged_phs_id_list.txt
	fi
fi

 
###############################################################################
# 2. Create a manifest from a bucket
GIT_ORG_TO_PR_TO=$(jq -r .git_org_to_pr_to <<< $CREDS_JSON)
GIT_REPO_TO_PR_TO=$(jq -r .git_repo_to_pr_to <<< $CREDS_JSON)
GITHUB_USER_EMAIL=$(jq -r .github_user_email <<< $CREDS_JSON)
GITHUB_USER_NAME=$(jq -r .github_user_name <<< $CREDS_JSON)
GITHUB_PERSONAL_ACCESS_TOKEN=$(jq -r .github_personal_access_token <<< $CREDS_JSON)
export GITHUB_TOKEN=$GITHUB_PERSONAL_ACCESS_TOKEN

if [ "$CREATE_GENOME_MANIFEST" == "true" ]; then
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

	# TODO: delete this line
	rm /dataSTAGE-data-ingestion/genome_file_manifest.csv

	cd /dataSTAGE-data-ingestion/scripts/
	echo $GS_CREDS_JSON >> gs_cloud_key.json
	gcloud auth activate-service-account --key-file=gs_cloud_key.json  --project=$GCP_PROJECT_ID
	gsutil ls
	GCP_PROJECT_ID=$GCP_PROJECT_ID ./generate-file-manifest.sh > ../genome_file_manifest.csv
fi

###############################################################################
# 3. Create extract file
cd / && git clone https://github.com/uc-cdis/dbgap-extract.git
cd dbgap-extract
# TODO: alter these 2 lines to use master branch
git checkout feat/validate-extract
git pull origin feat/validate-extract
pipenv install
pipenv run python3 dbgap_extract.py --study_accession_list_filename $PHS_ID_LIST_PATH --output_filename generated_extract.tsv > /dev/null 2>&1

# If the step is successful, don't print its output
extract_step_failed=$?
if [ $extract_step_failed -eq 1 ]; then
    cat generated_extract.log
fi

###############################################################################
# 4. Generate a list of commands to create Google Groups and a mapping file for the joindure script
cd /dataSTAGE-data-ingestion/scripts/
if [ ! -d "joindure/output" ]; then
	mkdir joindure/output
fi
python3 generate_google_group_cmds.py --extract_filename /dbgap-extract/generated_extract.tsv
if [ -f "google-groups.sh" ]; then
  chmod +x google-groups.sh
  mv google-groups.sh /dataSTAGE-data-ingestion/scripts/joindure/output/google-groups.sh
fi
mv mapping.txt /dataSTAGE-data-ingestion/scripts/joindure/mapping.txt

###############################################################################
# 5. Run joindure script
cd /dataSTAGE-data-ingestion/scripts/joindure

pipenv run python3 main.py merge --genome_manifest /dataSTAGE-data-ingestion/genome_file_manifest.csv \
    --dbgap_extract_file /dbgap-extract/generated_extract.tsv --out output

cp /dataSTAGE-data-ingestion/scripts/fence-image-commands.sh /dataSTAGE-data-ingestion/scripts/joindure/output
ls output

###############################################################################
# 6. Make PR to repo with outputs
cd /
git config --global user.email $GITHUB_USER_EMAIL
git clone "https://$GITHUB_USER_NAME:$GITHUB_PERSONAL_ACCESS_TOKEN@github.com/$GIT_ORG_TO_PR_TO/$GIT_REPO_TO_PR_TO.git"

cd $GIT_REPO_TO_PR_TO

git pull origin master && git fetch --all
BRANCH_NAME_PREFIX='feat/release-'
RELEASE_NUMBER=$(python3 /dataSTAGE-data-ingestion/scripts/get_release_number.py --current_branches "$(git branch -a)")
git checkout -b "$BRANCH_NAME_PREFIX$RELEASE_NUMBER"
git pull origin master && git fetch --all
mkdir -p "release-$RELEASE_NUMBER/intermediate_files"
cd "release-$RELEASE_NUMBER"
cp -R /dataSTAGE-data-ingestion/scripts/joindure/output/. ./intermediate_files/
mv ./intermediate_files/release_manifest.tsv "./release_manifest_r$RELEASE_NUMBER.tsv"
cp /dbgap-extract/generated_extract.tsv "./intermediate_files/generated_extract_r$RELEASE_NUMBER.tsv"
cp /dbgap-extract/generated_extract.log "./intermediate_files/generated_extract_r$RELEASE_NUMBER.log"

# Attempt to avoid hitting GitHub's filesize limit
zip -r "./release_manifest_r$RELEASE_NUMBER.zip" "./release_manifest_r$RELEASE_NUMBER.tsv"
rm "./release_manifest_r$RELEASE_NUMBER.tsv"

git add . && git commit -m "feat: release manifest"
git push -u origin $BRANCH_NAME_PREFIX$RELEASE_NUMBER

hub pull-request -F- <<<"$BRANCH_NAME_PREFIX$RELEASE_NUMBER

This pull request was automatically generated by PlanXCyborg."
