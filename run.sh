###############################################################################
# 1. Create a manifest from a bucket
# GCP_PROJECT_ID=zakir-test-project ./generate-file-manifest.sh > genome_file_manifest.csv


###############################################################################
# 2. Create extract file
git clone https://github.com/uc-cdis/dbgap-extract.git
cd dbgap-extract
git checkout feat/validate-extract
git pull origin feat/validate-extract
pipenv install
pipenv run python3 dbgap_extract.py --study_accession_list_filename ../test_phs_list.txt --output_filename generated_extract.tsv
head -n 10 generated_extract.tsv


###############################################################################
# 3. Generate a list of commands to create Google Groups and a mapping file for the joindure script
python generate_google_group_cmds.py --extract_filename generated_extract.tsv
mv mapping.txt /dataSTAGE-data-ingestion/scripts/joindure/mapping.txt


###############################################################################
# 4. Run joindure script
cd /dataSTAGE-data-ingestion/scripts/joindure
mkdir output
pipenv run python3 main.py merge --genome_manifest /dataSTAGE-data-ingestion/genome_file_manifest.csv \
	--dbgap_manifest /dataSTAGE-data-ingestion/dbgap-extract/generated_extract.tsv --out output

ls output