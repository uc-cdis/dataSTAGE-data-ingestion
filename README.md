# DataSTAGE Data Ingestion Pipeline

This PR contains a Dockerfile executable to be run as a Kubernetes job which lives here: 
https://github.com/uc-cdis/cloud-automation/blob/master/kube/services/jobs/data-ingestion-job.yaml

If this executable is run successfully, a new pull request will be created with the job outputs in this repository https://github.com/uc-cdis/dataSTAGE-data-ingestion-private and new Google Groups may be created corresponding to the study_with_consent ids (of the form phs001234.c1).

Overview: 
The Dockerfile in this repo installs some package prereqs and then calls the pipeline script, `run.sh`. The output of run.sh is passed to a Fence sidecar image, which then creates the necessary Google Groups if they do not exist.

Steps in the pipeline (run.sh):
1. (Optional) Check for additional PHS ID inputs that should be included from the review process. This step runs a new script called add_studies_from_manual_review.py stored in this repo which takes a file called "data_requiring_manual_review.tsv" from the individual who runs the Kubernetes job and merges any PHS IDs from that list into the PHS ID list that will be processed in the following steps.
2. Create a manifest from a bucket. This step runs a script called generate-file-manifest.sh, which has been adapted without alteration from this repo: https://github.com/nhlbidatastage/Data-Manifest
3. Create extract file. This step scrapes the dbgap website using a script stored here: https://github.com/uc-cdis/dbgap-extract
4. Generate a list of commands to create Google Groups and a mapping file for the joindure script. This step uses a new script called generate_google_group_cmds.py stored in this repo which uses the extract output to create a mapping.txt file (important for the joindure script) and a google-groups.sh file (to later be run by the fence sidecar which is deployed with this job.)
5. Run joindure script. This script is stored in this repo in scripts/joindure.
6. Make PR to this repo with the outputs: https://github.com/uc-cdis/dataSTAGE-data-ingestion-private


This repo has a suite of unit tests which be run like so:

`cd scripts/tests`

`./test_all.sh`