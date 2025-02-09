# brightway-scripts
A collection of things that I use when working with the Brightway LCA framework.

For more complicated things, or projects with collaboration, I usually make a separate repo. Have a look at my public repo list.

## Contents

### ecoinvent-chemical_structures
- [webpage with structure gallery](https://stew-mcd.github.io/brightway-scripts/ecoinvent-chemical_structures_gallery.html)
- [code in `ecoinvent-chemical_structures/`](ecoinvent-chemical_structures)
- [images in `ecoinvent-chemical_structures/images/`](ecoinvent-chemical_structures/structures)

Automatically extract chemical structures from ecoinvent 3.10 and match them to the CAS numbers. The result is a gallery of images of the structures and their associated information, sorted by molecular weight.

### Assorted brightway scripts

- [import_ecoinvent.py](import_ecoinvent.py) 
  - the old way, from a local copy of the ecoinvent database
- [import_ecoinvent_with_interface.py](import_ecoinvent_with_interface.py)
  - the new way, using the ecoinvent interface
- [make_prospective_databases.py](make_prospective_databases.py)
  - make a bunch of future databases with premise and the IAM scenarios
- [clean_projects_and_databases.py](clean_projects_and_databases.py)
  - spring cleaning for your brightway projects