from itertools import product
import os
use_testing_dir = 0

if use_testing_dir:
    CUSTOM_BW2_DIR = os.path.join(os.path.expanduser("~"), "brightway25data-testing")
    if not os.path.exists(CUSTOM_BW2_DIR):
        os.makedirs(CUSTOM_BW2_DIR)
    os.environ["BRIGHTWAY2_DIR"] = CUSTOM_BW2_DIR

import bw2data as bd
import bw2io as bi
import bw2calc as bc
import ecoinvent_interface as ei

DELETE_PROJECT = True
IMPORT_RELEASES = True
VALIDATE_DBS = True

PROJECT = "default-311"
VERSIONS = ["3.1.1"]
SYSTEM_MODELS = ["cutoff"]  # , "consequential"]
DBS = list(product(VERSIONS, SYSTEM_MODELS))

settings = ei.Settings(username=ei.Settings().username, password=ei.Settings().password)

if DELETE_PROJECT and PROJECT in bd.projects and len(bd.projects) > 1:
    print(f"Deleting project {PROJECT}")
    bd.projects.delete_project(PROJECT, delete_dir=True)

bd.projects.set_current(PROJECT)

print(f"** Using project: {PROJECT} **")
print(f"\tbw2data version: {bd.__version__}")
print(f"\tbw2io version: {bi.__version__}")
print(f"\tbw2calc version: {bc.__version__}")
print(f"\tecoinvent_interface version: {ei.__version__}")

print(f"** Existing databases **")
print(bd.databases)

if IMPORT_RELEASES:
    print(f"** Importing releases **")
    # Loop through releases and system models
    for version, system_model in DBS:
        db_name = f"ecoinvent-{version}-{system_model}"
        if db_name not in bd.databases:
            print(f"** Importing: {db_name}")
            try:
                bi.import_ecoinvent_release(version=version, system_model=system_model)
                print(f"SUCCESS: {db_name}")
            except Exception as e:
                print(f"FAILURE: {db_name} - {e}")
                continue

if VALIDATE_DBS:
    # Check the databases
    print("** Checking databases **")
    dbs = [x for x in bd.databases if "biosphere" not in x]
    for db_name in dbs:
        print(f"Checking {db_name}")
        try:
            db = bd.Database(db_name)
            print(f"\t{db}")
            # logging.info(f"{db}: \n{bd.Database(db).metadata}")
            score = 0
            attempt = 0
            while score == 0 and attempt <= 10:
                attempt += 1
                lca = bc.LCA({db.random(): 1}, bd.methods.random())
                lca.lci()
                lca.lcia()
                score = lca.score
                print(f"\t {lca.demand}\n\t {lca.method} \n\t {lca.score:.2e}")
        except Exception as e:
            print(f"FAILURE VALIDATING: {db} : {e}")
        if attempt == 10:
            print(f"** {db_name}: produced {attempt} zero scores **")
            print("\tProbably something is wrong here...")

print("Done")
