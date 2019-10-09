#!/bin/bash
set -uo pipefail

if [[ $# -gt 0 && $1 == "-h" ]]; then
  echo 'Usage: GCP_PROJECT_ID=<billing_project> ./generate-file-manifest.sh > file-manifest.csv'
  exit 0
fi

if [[ -z "$(which gsutil)" ]]; then
  (>&2 echo "Error: you must install and authenticate gsutil CLI")
  exit -1
fi

if [[ -z "$(which aws)" ]]; then
  (>&2 echo "Error: you must install and authenticate aws CLI")
  exit -1
fi

if [[ ! -v GCP_PROJECT_ID ]]; then
  (>&2 echo "Error: you must set GCP_PROJECT_ID environment variable to access requester pays bucket")
  exit -1
fi

tmp_dir=`mktemp -d`

gcp_file_list=${tmp_dir}/gcp_files.txt
aws_file_list=${tmp_dir}/aws_files.txt

rc=0

if true; then
#exit -1
# aws s3 ls s3://nih-nhlbi-datacommons/ > ${aws_file_list} &&
aws s3 ls s3://devplanetv1-proj1-databucket-gen3/
echo "generate-file-manifest.sh line 35"
aws s3 ls s3://devplanetv1-proj1-databucket-gen3/ > ${aws_file_list} &&
gsutil -u ${GCP_PROJECT_ID} ls -L gs://topmed-irc-share/genomes/ |
  grep "^gs://\|^    Content-Length\|^    Hash (md5)" | 
  paste - - - | 
  awk '{print substr($1, 1, length($1)-1)","$3","$6}' > ${gcp_file_list}
rc=$?
fi

join_cmd='join -a1 -a2 -o auto -t'','''

if [[ $rc == 0 ]]; then
  awk -F '[/,]' '{print $5","$0}' $gcp_file_list | grep "^NWD" | sort -t',' -k1,1 > ${tmp_dir}/gcp_manifest.csv &&
  cat $aws_file_list | rev | cut -f1 -d' ' | rev | awk -F '[/,]' '{print $1",s3://nih-nhlbi-datacommons/"$0}' | grep "^NWD" | sort -t',' -k1,1 > ${tmp_dir}/aws_manifest.csv &&
  printf "sample_id,aws_uri,gcp_uri,file_size,md5\n" &&
  ${join_cmd} ${tmp_dir}/aws_manifest.csv ${tmp_dir}/gcp_manifest.csv | awk -F '.' '{print $1","$0}' | cut -f1,3- -d','
  rc=$?
fi

rm -r ${tmp_dir}
exit $rc