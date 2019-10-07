###############################################################################
# 1. Create a manifest from a bucket
ls ~
ls ~/.aws/
cat ~/.aws/config

GCP_PROJECT_ID=zakir-test-project ./generate-file-manifest.sh > genome_file_manifest.csv

exit

###############################################################################
# 2. Create extract file
git clone https://github.com/uc-cdis/dbgap-extract.git
cd dbgap-extract
git checkout feat/validate-extract
git pull origin feat/validate-extract
cd ./dbgap-extract

pipenv install
pipenv run python3 dbgap_extract.py --study_accession_list_filename ../test_phs_list.txt --output_filename generated_extract.tsv

head -n 10 generated_extract.tsv

###############################################################################
# 3. Run joindure script
cd /dataSTAGE-data-ingestion/scripts
ls ..
ls
mkdir output
pipenv run python3 main.py merge --genome_manifest ../genome_file_manifest.csv --dbgap_manifest ../dbgap-extract/generated_extract.tsv --out output

ls output

###############################################################################
# 4. Generate a list of commands to create Google Groups



###############################################################################