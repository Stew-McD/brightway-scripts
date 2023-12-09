import os
import logging
from random import choice, shuffle

CUSTOM_BW2_DIR = os.path.join(os.path.expanduser("~"), "brightway2data-testing")
LOG_FILE = "import_ecoinvent_release.log"
PROJECT = "default-test"
DELETE_PROJECT = False
IMPORT_RELEASES = True
IMPORT_LIMIT = 20
VALIDATE_DBS = True

if not os.path.exists(CUSTOM_BW2_DIR):
    os.makedirs(CUSTOM_BW2_DIR)
os.environ["BRIGHTWAY2_DIR"] = CUSTOM_BW2_DIR

import bw2data as bd
import bw2io as bi
import bw2calc as bc
import ecoinvent_interface as ei

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)

settings = ei.Settings(username=ei.Settings().username, password=ei.Settings().password)
release = ei.EcoinventRelease(settings)

if DELETE_PROJECT and PROJECT in bd.projects:
    print(f"Deleting project {PROJECT}")
    bd.projects.delete_project(PROJECT, delete_dir=True)

bd.projects.set_current("default-test")

# Logging basic info
logging.info("Importing ecoinvent releases")
logging.info(f"\tbw2data version: {bd.__version__}")
logging.info(f"\tbw2io version: {bi.__version__}")
logging.info(f"\tecoinvent_interface version: {ei.__version__}")

if IMPORT_RELEASES:
    # Loop through releases and system models
    import_count = 0
    releases = release.list_versions()
    shuffle(releases)
    for version in releases[:IMPORT_LIMIT]:
        system_model = choice(release.list_system_models(version))
        db_name = f"ecoinvent-{version}-{system_model}"
        if db_name not in bd.databases:
            logging.info(f"Importing {version} {system_model}")
            print(f"\t** Importing {version} {system_model} **")
            try:
                bi.import_ecoinvent_release(version=version, system_model=system_model)
                logging.info(f"SUCCESS: {version} - {system_model}")
                import_count += 1
            except Exception as e:
                logging.error(f"FAILURE: {version} - {system_model}")
                logging.exception("Exception occurred")  # This will log the traceback
                continue

if VALIDATE_DBS:
    # Check the databases
    logging.info("Checking databases")
    dbs = [x for x in bd.databases if "biosphere" not in x]
    for db_name in dbs:
        print(f"Checking {db_name}")
        try:
            db = bd.Database(db_name)
            logging.info(f"{db}")
            print(f"\t{db}")
            # logging.info(f"{db}: \n{bd.Database(db).metadata}")
            score = 0
            attempt = 0
            while score == 0 and attempt < 10:
                attempt += 1
                lca = bc.LCA({db.random(): 1}, bd.methods.random())
                lca.lci()
                lca.lcia()
                score = lca.score
                print(f"\t {lca.demand}\n\t {lca.method} \n\t {lca.score:.2e}")
        except Exception as e:
            logging.error(f"FAILURE VALIDATING: {db} : {e}")
            print(f"FAILURE VALIDATING: {db} : {e}")

print("Done")
