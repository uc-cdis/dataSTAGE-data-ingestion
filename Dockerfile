FROM python:alpine

RUN apk update && apk add --no-cache ca-certificates gcc musl-dev git jq curl bash

RUN git clone https://github.com/uc-cdis/dbgap-extract.git

WORKDIR /dbgap-extract

# TODO: determine if the file should live in this repo or not (bc it was created by an external collaborator)
# RUN ./generate-file-manifest.sh --out_file genome_file_manifest.csv

RUN python dbgap_extract.py --study_accession_list_filename phs_list.txt --output_filename generated_extract.tsv

# validation not necessary right?
# RUN python validate_extract.py --input_file phs_list.txt --output_file generated_extract.tsv

RUN mkdir output
RUN python3 main.py merge --genome_manifest ../../genome_file_manifest.csv --dbgap_manifest ../../../generated_extract.tsv --out output

# COPY run.sh run.sh

# CMD [ "/bin/bash", "./run.sh"]
