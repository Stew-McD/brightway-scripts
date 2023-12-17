# ecoinvent-chemical_structures

## Why, what, how?

When building LCA inventories of chemical processes, it is sometimes necessary to use proxy chemicals to represent some of the inputs and outputs that cannot be found in the database. When this is the case, it is important to ensure that the proxy chemicals are as similar as possible to the real chemicals that they are replacing.

Usually, one would need to search on the internet to see the structures of the chemicals, which are sometimes listed in the database under non-systematic names that give no hint to the structure. This gets rather annoying, and makes it easier to miss the best match or choose the wrong proxy.

To make this process easier, I have processed the ecoinvent 3.10 database to extract the chemical abstract (CAS) numbers and (where possible) match each one to its structure. This allows one to do a quick visual scan through the structures to find the most appropriate proxy. Additional chemical information is also obtained, such as the SMILES string and the InChI code, formulas, and molecular weights and synonyms.

The source code, data and images related to processing the database and collecting the structures is available on [GitHub](https://github.com/Stew-McD/brightway-scripts/blob/main/ecoinvent-chemical_structures/)

## The structures

(THE GIT PAGE BUILD IS NOT WORKING RIGHT, BUT YOU CAN DOWNLOAD THE IMAGES FROM THE REPO AND VIEW THEM LOCALLY)

On [this page](/home/chemical_structures_gallery.html) you can find the images of the structures, sorted by molecular weight. The images are in SVG format, and are named `<mW>_<CAS>.svg`, where `<mW>` is the rounded molecular weight and `<CAS>` is the CAS number. Each image is annotated with the CAS number, ecoinvent name, IUPAC name, smiles string, formula and synonyms.

The svg text SHOULD be searchable, so you can hit ctrl+f and search for whatever you are looking for and see the scructure and other infomation instantly. (NOT WORKING RIGHT NOW)

Ideally this presentation would be interactive somehow, with filtering and sorting options, but I don't have the time to do that right now. If you want to do it, feel free to fork the repo and make a pull request.
