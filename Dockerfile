FROM python:alpine

COPY test_phs_list.txt /test_phs_list.txt

RUN apk update && apk add --no-cache ca-certificates gcc musl-dev git jq curl bash

RUN pip3 install --upgrade pip && pip3 install pipenv

###############################################################################
# 1. Create a manifest from a bucket
# TODO: determine if the file should live in this repo or not (bc it was created by an external collaborator)

# RUN ./generate-file-manifest.sh --out_file genome_file_manifest.csv

###############################################################################
# 2. Create extract file

RUN git clone https://github.com/uc-cdis/dbgap-extract.git && cd dbgap-extract && git checkout feat/validate-extract && git pull origin feat/validate-extract

WORKDIR /dbgap-extract

# COPY ../test_phs_list.txt ./test_phs_list.txt

RUN pipenv install

RUN pipenv run python3 dbgap_extract.py --study_accession_list_filename ../test_phs_list.txt --output_filename generated_extract.tsv

RUN head -n 10 generated_extract.tsv

# validation not necessary right?
# RUN python validate_extract.py --input_file ../test_phs_list.txt --output_file generated_extract.tsv

###############################################################################
# 3. Run joindure script
RUN mkdir output

WORKDIR ..

# RUN pipenv run python3 main.py merge --genome_manifest genome_file_manifest.csv --dbgap_manifest dbgap-extract/generated_extract.tsv --out output

###############################################################################
# 4. Create Google Groups



###############################################################################