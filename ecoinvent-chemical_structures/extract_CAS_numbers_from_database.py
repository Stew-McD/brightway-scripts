import bw2io as bi
import bw2data as bd
import csv
PROJECT = "default-test-cas"
DATABASE = "ecoinvent-3.10-cutoff"

# this uses an edited version of bw2io to add also the CAS number to the database if it is in the .spold file. only two lines need to be added to the code in `eco_spold2.py` (589-590):
# `        if exc.get("casNumber"):
#            data["CAS number"] = exc.get("casNumber")`
            

bd.projects.set_current(PROJECT)

if DATABASE not in bd.databases:
    bi.import_ecoinvent_release(
        version="3.10",
        system_model="cutoff",
    )

db = bd.Database("ecoinvent-3.10-cutoff")

# loop through all activities and exchanges and add the CAS number to a dictionary
dict_cas = {}
for act in db:
    for exc in act.exchanges():
        if exc.get("type") == "production" and exc.get("CAS number"):
            dict_cas[exc.get("name")] = exc.get("CAS number").lstrip("0")
            print(f'{exc.get("name"): <40} {exc.get("CAS number")}')

# Save dict_cas as a CSV file
with open(f'{DATABASE.replace(".","")}_CAS_numbers.csv', 'w') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['name', 'CAS number'])
    for key, value in dict_cas.items():
        writer.writerow([key, value.lstrip("0")])


