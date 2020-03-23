# Exit if any command fails
set -e
set -o pipefail

###############################################################################
# 1. (Optional) Check for additional PHS ID inputs that should be included from the review process
PHS_ID_LIST_PATH=/phs-id-list/phsids.txt
DATA_FROM_MANUAL_REVIEW='/dataSTAGE-data-ingestion/data_requiring_manual_review.tsv'

if [ -d "/data-from-manual-review/" ]; then
	files_in_manual_review_mount=( /data-from-manual-review/* )
	if [ ${#files_in_manual_review_mount[@]} -ge 1 ]; then
		DATA_FROM_MANUAL_REVIEW=/data-from-manual-review/data_requiring_manual_review.tsv
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

if [ "$CREATE_GENOME_MANIFEST" == "true" ]; then
	echo 'Genome file manifest not found. Creating one...'
	GS_CREDS_JSON=$(jq -r .gs_creds <<< $CREDS_JSON)
	GCP_PROJECT_ID=$(jq -r .gcp_project_id <<< $CREDS_JSON)
	cd /dataSTAGE-data-ingestion/scripts/
	echo $GS_CREDS_JSON >> gs_cloud_key.json
	gcloud auth activate-service-account --key-file=gs_cloud_key.json  --project=$GCP_PROJECT_ID
	GCP_PROJECT_ID=$GCP_PROJECT_ID ./generate-file-manifest.sh > ../genome_file_manifest.csv
	GENOME_FILE_MANIFEST_PATH=../genome_file_manifest.csv
else
	echo 'Skipping genome file manifest creation step...'
	BUCKET_NAME=$(jq -r .local_data_aws_creds.bucket_name <<< $CREDS_JSON)
	aws s3 cp "s3://$BUCKET_NAME/genome_file_manifest.csv" /dataSTAGE-data-ingestion/genome_file_manifest.csv
fi

###############################################################################
# 3. Create extract file
cd / && git clone https://github.com/uc-cdis/dbgap-extract.git
cd dbgap-extract
git pull origin master

# get the latest release/tag
git fetch --tags
tag=$(git describe --tags `git rev-list --tags --max-count=1`)
git checkout $tag -b latest

pipenv install
pipenv run python3 dbgap_extract.py --study_accession_list_filename $PHS_ID_LIST_PATH --output_filename generated_extract.tsv > /dev/null 2>&1

# If the step is successful, don't print its output
extract_step_failed=$?
if [ $extract_step_failed -eq 1 ]; then
    cat generated_extract.log
fi

###############################################################################
# 4. Generate a list of commands to create Google Groups and a mapping file for the manifestmerge script
cd /dataSTAGE-data-ingestion/scripts/
if [ ! -d "manifestmerge/output" ]; then
	mkdir manifestmerge/output
fi
python3 generate_google_group_cmds.py --dbgap_extract /dbgap-extract/generated_extract.tsv
if [ -f "google-groups.sh" ]; then
  chmod +x google-groups.sh
  mv google-groups.sh /dataSTAGE-data-ingestion/scripts/manifestmerge/output/google-groups.sh
fi
mv studies_to_google_access_groups.txt /dataSTAGE-data-ingestion/scripts/manifestmerge/studies_to_google_access_groups.txt

###############################################################################
# 5. Run manifestmerge script
cd /dataSTAGE-data-ingestion/scripts/manifestmerge

pipenv run python3 main.py --genome_manifest /dataSTAGE-data-ingestion/genome_file_manifest.csv \
    --dbgap_extract_file /dbgap-extract/generated_extract.tsv \
		--studies_to_google_access_groups studies_to_google_access_groups.txt --out output

cp /dataSTAGE-data-ingestion/scripts/fence-image-commands.sh /dataSTAGE-data-ingestion/scripts/manifestmerge/output
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
cp -R /dataSTAGE-data-ingestion/scripts/manifestmerge/output/. ./intermediate_files/
mv ./intermediate_files/release_manifest.tsv "./release_manifest.tsv"
cp /dbgap-extract/generated_extract.tsv "./intermediate_files/dbgap_extract.tsv"
cp /dbgap-extract/generated_extract.log "./intermediate_files/dbgap_extract.log"
cp $PHS_ID_LIST_PATH ./intermediate_files/phsids.txt
cp /dataSTAGE-data-ingestion/genome_file_manifest.csv ./


# Attempt to avoid hitting GitHub's filesize limit
zip -r "./release_manifest_r$RELEASE_NUMBER.zip" "./release_manifest.tsv"
rm ./release_manifest.tsv
zip -r "./intermediate_files/data_requiring_manual_review.zip" "./intermediate_files/data_requiring_manual_review.tsv"
rm ./intermediate_files/data_requiring_manual_review.tsv
gzip genome_file_manifest.csv
rm intermediate_files/fence-image-commands.sh

git add . && git commit -m "feat: release manifest"
git push -u origin $BRANCH_NAME_PREFIX$RELEASE_NUMBER

hub pull-request -F- <<<"$BRANCH_NAME_PREFIX$RELEASE_NUMBER

This pull request was automatically generated by PlanXCyborg."
