# TODO: automate the ingestion of the PHIs from the dbgap_extract output, write the output to a shell script, put this in version control

import subprocess

def generate_cmd_sets(studies):
	commands = []
	for study_accession_with_consent in studies:
		link_external_bucket_cmd = "fence-create link-external-bucket --bucket-name {}".format(
			study_accession_with_consent
		)
		commands.append(link_external_bucket_cmd)
	
	for study_accession_with_consent in studies:
		link_to_gen3_project_cmd = "fence-create link-bucket-to-project --bucket_id {} --bucket_provider google --project_auth_id {}".format(
			study_accession_with_consent, study_accession_with_consent
		)
		commands.append(link_to_gen3_project_cmd)

	for study_accession_with_consent in studies:
		link_to_topmed_cmd = "fence-create link-bucket-to-project --bucket_id {} --bucket_provider google --project_auth_id topmed".format(
			study_accession_with_consent, study_accession_with_consent
		)
		commands.append(link_to_topmed_cmd)

	for study_accession_with_consent in studies:
		link_all_projects_cmd = "fence-create link-bucket-to-project --bucket_id allProjects --bucket_provider google --project_auth_id {}".format(
			study_accession_with_consent, study_accession_with_consent
		)
		commands.append(link_all_projects_cmd)

	return commands

def make_mapping_entry_for_study(study_with_consent):
	print("{}: stagedcp_ {}_read_gbag@dcp.bionimbus.org".format(
		study_with_consent, study_with_consent
	))

def dedup():
	f = open('dedupme')
	r = f.readlines()
	# print(len(r))
	f.close()
	dict_of_things = {}
	for thing in r:
		if 'phs' not in thing:
			continue
		dict_of_things[thing.strip()] = 1
	rv = dict_of_things.keys()
	rv.sort()
	print(rv)

# studies = ['phs000007.c1', 'phs000007.c2', 'phs000179.c1', 'phs000179.c2', 'phs000200.c1', 'phs000200.c2', 'phs000280.c1', 'phs000280.c2', 'phs000284.c1', 'phs000286.c1', 'phs000286.c2', 'phs000286.c3', 'phs000286.c4', 'phs000287.c1', 'phs000287.c2', 'phs000287.c3', 'phs000287.c4', 'phs000289.c1', 'phs000741.c1', 'phs000784.c1', 'phs000820.c1', 'phs000914.c1', 'phs000920.c2', 'phs000921.c2', 'phs000946.c1', 'phs000951.c1', 'phs000951.c2', 'phs000954.c1', 'phs000956.c2', 'phs000972.c1', 'phs000974.c1', 'phs000974.c2', 'phs000988.c1', 'phs000993.c1', 'phs000993.c2', 'phs000997.c1', 'phs001001.c1', 'phs001001.c2', 'phs001013.c1', 'phs001013.c2', 'phs001024.c1', 'phs001032.c1', 'phs001040.c1', 'phs001062.c1', 'phs001062.c2', 'phs001074.c2', 'phs001161.c1', 'phs001180.c2', 'phs001189.c1', 'phs001207.c1', 'phs001215.c1', 'phs001217.c1', 'phs001218.c2', 'phs001237.c1', 'phs001237.c2', 'phs001238.c1', 'phs001293.c1', 'phs001293.c2', 'phs001345.c1', 'phs001359.c1', 'phs001387.c3', 'phs001402.c1', 'phs001412.c1', 'phs001412.c2', 'phs001416.c1', 'phs001416.c2']

def main():
    parser = argparse.ArgumentParser(description="Generate set of fence-create commands for study-related Google Groups.")
    parser.add_argument(
        "--extract_filename",
        help="a generated dbgap extract file",
    )

    args = parser.parse_args(sys.argv[1:])

    if args.study_accession_list_filename:
        logging.debug("-------")
        logging.debug(
            "Usage error. Run this script using the below command form:"
        )
        logging.debug(
            "> python generate_google_group_cmds.py --extract_filename <filename.tsv>"
        )
        logging.debug("-------")
        exit(0)

    
    f = open(args.extract_filename)
    records = f.readlines()
    print(records[:5])
    study_accessions = list(map(lambda x: x.split(), studies_to_scrape))
    f.close()

    output_filename = FILENAME + ".tsv"

    logging.debug(
        "Extracting the below studies to {} \n".format(output_filename)
        + " ".join(studies_to_scrape)
    )

    scrape(studies_to_scrape, output_filename)

	commands = generate_cmd_sets(studies)

	logging.debug("All done. Extracted elements to {}".format(output_filename))