# This file is used specifically to set variables that must be exported.
# Usage: source ./setup_env.sh

GITHUB_PERSONAL_ACCESS_TOKEN=$(jq -r .github_personal_access_token <<< $CREDS_JSON)
export GITHUB_TOKEN=$GITHUB_PERSONAL_ACCESS_TOKEN

if [ "$CREATE_GENOME_MANIFEST" == "true" ]; then
	export AWS_ACCESS_KEY_ID=$(jq -r .genome_bucket_aws_creds.aws_access_key_id <<< $CREDS_JSON)
	export AWS_SECRET_ACCESS_KEY=$(jq -r .genome_bucket_aws_creds.aws_secret_access_key <<< $CREDS_JSON)
	AWS_SESSION_TOKEN=$(jq -r .genome_bucket_aws_creds.aws_session_token <<< $CREDS_JSON)
	if [[ -z "$AWS_SESSION_TOKEN" ]]; then
	  export AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN
	fi
else
	export AWS_ACCESS_KEY_ID=$(jq -r .local_data_aws_creds.aws_access_key_id <<< $CREDS_JSON)
	export AWS_SECRET_ACCESS_KEY=$(jq -r .local_data_aws_creds.aws_secret_access_key <<< $CREDS_JSON)
fi