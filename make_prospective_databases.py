import os
from pathlib import Path
from itertools import product
from itertools import zip_longest

import premise as pm
import bw2data as bd

SCENARIO_DIR = pm.filesystem_constants.DATA_DIR / "iam_output_files"
filenames = sorted([x for x in os.listdir(SCENARIO_DIR) if x.endswith(".csv")])

FILE_LOG = 'make_prospective_databases.log'

# ---------------------------------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------------------------------

# Mostly you just need to change these variables
project_name = "default"
source_db = "ecoinvent_3.9.1_consequential"
new_project = (
    source_db + "-premise"
)  # if you want to make a new project, leave a string, otherwise "None"

bd.projects.set_current(project_name)

if new_project:
    bd.projects.copy_project(new_project)

# other variables you can change if you want
premise_key = "tUePmX_S5B8ieZkkM7WUU2CnO8SmShwmAeWK9x2rTFo="
batch_size = (
    5  # number of scenarios to process at once (change this if you have memory issues)
)
keep_uncertainty = True
multiprocessing = True  # use multiprocessing (True) or not (False) (change this if you there are problems)
premise_quiet = (
    True  # if you want to see the output of the premise functions (True) or not (False)
)


# CHOOSE SCENARIOS
# Comment out the scenarios you don't want to use, otherwise all potential scenarios will be attempted
# The full list of available scenarios is in the `filenames` variable (atm 15, but there could be more in future updates)
# Not all combinations are available, later, we will filter out the scenarios that are not possible

models = [
    "image",
    "remind",
]

ssps = [
    # "SSP1",
    "SSP2",
    # "SSP5",
]

rcps = [
    "Base",  # choose the rcp you want to use, (mostly this comment is to stop the linter from removing the line breaks)
    "RCP19",
    "RCP26",
    "NPi",
    "NDC",
    "PkBudg500",
    "PkBudg1150",
]

# If the years you put here are inside the range of the scenario, in will interpolate the data, otherwise, probably it fails. Most of the scenarios are between 2020 and 2100, I think.

years = [
    # 2020,
    # 2025,
    # 2030,
    # 2035,
    # 2040,
    # 2045,
    2050,
]

# this part makes all the possible combinations of the scenarios you want to use, the next part will filter out the ones that are not available

desired_scenarios = []
for model, ssp, rcp in product(models, ssps, rcps):
    desired_scenarios.append({"model": model, "pathway": ssp + "-" + rcp})

# ---------------------------------------------------------------------------------
# FILTER OUT SCENARIOS THAT ARE NOT AVAILABLE
# ---------------------------------------------------------------------------------

# Split the string and extract the version number
parts = source_db.split("_")
source_version = parts[1] if "." in parts[1] else parts[1].split(".")[0]
source_systemmodel = parts[-1]


# function to make arguments for "new database -- pm.nbd" based on possible scenarios
def make_possible_scenario_list(filenames, desired_scenarios, years):
    possible_scenarios = []
    for filename in filenames:
        climate_model = filename.split("_")[0]
        ssp = filename.split("_")[1].split("-")[0]
        rcp = filename.split("_")[1].split("-")[1].split(".")[0]
        possible_scenarios.append({"model": climate_model, "pathway": ssp + "-" + rcp})

    # scenarios = overlap of desired_scenarios and possible_scenarios
    scenarios = [x for x in desired_scenarios if x in possible_scenarios]

    # now add the years
    scenarios = [{**scenario, "year": year} for scenario in scenarios for year in years]

    return scenarios


scenarios = make_possible_scenario_list(filenames, desired_scenarios, years)


# ---------------------------------------------------------------------------------
# MAKE PREMISE DATABASES
# ---------------------------------------------------------------------------------

os.makedirs(
    "premise_data", exist_ok=True
)  # make a folder for it, or premise makes a mess
os.chdir("premise_data")


# Function to split scenarios into smaller groups (for batch processing)
def grouper(iterable, batch_size, fillvalue=None):
    args = [iter(iterable)] * batch_size
    return zip_longest(*args, fillvalue=fillvalue)


print(f'{"-"*80}')
print(
    f"\n** Making prospective dbs with: {source_db} in project: {bd.projects.current} **\n"
)
print(f'{"-"*80}')

with open(FILE_LOG, "a") as f:
    f.write(f"Making prospective dbs with: {source_db} in project: {bd.projects.current}\n")

for scenario in scenarios:
    print(f"\t\t **  {scenario}")


# function to make the databases
def make_premise_dbs(
    scenarios,
    source_db,
    source_version,
    source_systemmodel,
    premise_key,
    batch_size,
):
    count = 0

    # Loop through scenario batches
    for scenarios_set in grouper(scenarios, batch_size):
        if len(scenarios) < batch_size:
            total_batches = 1
            scenarios_set = scenarios

        else:
            total_batches = len(scenarios) // batch_size

        count += 1
        print(
            f"\n ** Processing scenario set {count} of {total_batches: .0f}, batch size {batch_size} **"
        )

        # THIS IS THE STANDARD SET FOR THE CONSEQUALTIAL MODEL, CHANGE AS NEEDED
        # FOR THE CUTOFF MODEL, IT HAS NO EFFECT
        if source_systemmodel == "cutoff":
            model_args = None

        else:
            model_args = {
                "range time": 2,
                "duration": False,
                "foresight": False,
                "lead time": True,
                "capital replacement rate": False,
                "measurement": 0,
                "weighted slope start": 0.75,
                "weighted slope end": 1.00,
            }

        # Create new database based on scenario details
        ndb = pm.NewDatabase(
            key=premise_key,
            scenarios=scenarios_set,
            source_db=source_db,
            source_version=source_version,
            system_model=source_systemmodel,
            use_multiprocessing=multiprocessing,
            keep_uncertainty_data=keep_uncertainty,
            system_args=model_args,
            quiet=premise_quiet,
            gains_scenario="CLE",
            use_absolute_efficiency=False,
            additional_inventories=None,
        )

        # Define the list of methods to call, some are included in all, but may as well try them all just in case
        updates = [
            ndb.update_all,
            ndb.update_cars,
            ndb.update_buses,
            ndb.update_two_wheelers,
            ndb.update_electricity,
            ndb.update_cement,
            ndb.update_steel,
            ndb.update_fuels,
            ndb.update_emissions,
            ndb.update_dac,
        ]

        # Call each method inside a try/except block
        for update in updates:
            try:
                update()
            except Exception as e:
                print(f"Failed to update with {update.__name__}: {e}")
                with open(FILE_LOG, "a") as f:
                    f.write(f"Failed to update with scenario {scenario}, {update.__name__}: {e}\n")

        # Write the new database to brightway
        try:
            ndb.write_db_to_brightway()
            with open(FILE_LOG, "a") as f:
                f.write(f"Successfully wrote database {scenario} to brightway\n")
        except Exception as e:
            print(f"Failed to write database to brightway: {e}")
            with open(FILE_LOG, "a") as f:
                f.write(f"Failed to write database {scenario} to brightway: {e}\n")

    # Add GWP factors to the project
    pm.add_premise_gwp()
    print("***** Done! *****")

    # change back to the original directory
    os.chdir(Path(__file__).parent)

    print(f"{'='*80}")
    print(f'{"-"*80}')
    print(f"\n** Finished making prospective dbs with: {source_db} **\n")
    print(f'{"-"*80}')
    print(f"{'='*80}")


if __name__ == "__main__":
    make_premise_dbs(
        scenarios,
        source_db,
        source_version,
        source_systemmodel,
        premise_key,
        batch_size,
    )
