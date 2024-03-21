import os
import bw2data as bd
from pathlib import Path
from tabulate import tabulate

DELETE = 1

HOME = Path.home()
bwstrings = ["bw", "brightway"]
bw2list = [x for x in os.listdir(HOME) if any(s in x for s in bwstrings)]

# output of bw2list
BW2DIRS = ["brightway25data-testing", 
           "brightway2data-testing",
            "brightway25data", 
            "brightway2data"]

BW2DIRS = [os.path.join(HOME, x) for x in BW2DIRS]

# print a report for each directory
BW2DIR = BW2DIRS[3]  # choose here

print(f"Using: {BW2DIR}")
os.environ["BRIGHTWAY2_DIR"] = BW2DIR
assert os.environ.get("BRIGHTWAY2_DIR") == BW2DIR, "BRIGHTWAY2_DIR not set correctly"
import bw2data as bd

# Prepare data for tabulate
table_data = [(name, dbs, round(size, 2)) for name, dbs, size in bd.projects.report()]
headers = ["Name", "DBs", "Size (GB)"]

# Print the table
print("Projects:")
print(tabulate(table_data, headers=headers))
project_list = [x[0] for x in table_data]

# output of project_list
DELETE_LIST = [
    "SSP-cutoff",
    "SSP2-cutoff",
    "SSP2LT-cutoff",
    "T-reX-premise-SSP2-cutoff",
    "T-reX-SSP2-cutoff",
    # "default",
]

if DELETE:
    print(f'{"-"*60}')
    print("Deleting projects")
    for project in DELETE_LIST:
        if project not in project_list:
            print(f"\t - Can't delete: {project},  not found")
            continue
        print(f"\t + Deleting {project}")
        bd.projects.delete_project(project, delete_dir=True)

    # check that it worked
    print(f'{"-"*60}')
    print("Checking that it worked")
    table_data = [(name, dbs, round(size, 2)) for name, dbs, size in bd.projects.report()]

    # Print the table
    print("Projects:")
    print(tabulate(table_data, headers=headers))
