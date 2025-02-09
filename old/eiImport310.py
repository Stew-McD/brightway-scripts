#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 11:02:52 2022

@author: stew
"""

"""
First, setup a virtual environment in your terminal

add channels to your pip



cd <where you want to put it>

for automatic dl
python env -m bw2ei38 eidl bw2io==0.8.7 bw2speedups pypardiso
or
python env -m bw2ei38 eidl bw2io==0.8.7 bw2speedups pypardiso


then
python env -m bw2ei38 brightway2 bw2io==0.8.7 bw2speedups
or
python env -m bw2ei39 brightway2 bw2io==0.8.8 bw2speedups

or with conda
conda install -c conda-forge -c cmutel brightway2 bw2io=0.8.7 bw2speedups pypardiso
conda install -c conda-forge -c cmutel brightway2 bw2io=0.8.8 bw2speedups pypardiso

then,
source bw2ei38/bin/activate

then run this python script cell by cell..

"""

#%%

import os
# os.environ["BRIGHTWAY2_DIR"] = os.path.expanduser("~") +"/brightway2"

from py7zr import SevenZipFile
import bw2io as bi
import bw2data as bd

db_dir = "/home/stew/CML/code/DBs/EI/"
db_files = [x for x in os.listdir(db_dir) if "ecoinvent_3.10" in x]

PROJ_NAME = "default"
delete_existing = False
report = False

print("** Let's try to import ecoinvent... **")
print(f'bw2io version = {bi.__version__}')
print(f'bw2data version = {bd.__version__}')


if delete_existing:
        if PROJ_NAME in bd.projects: 
            bd.projects.delete_project(PROJ_NAME, True)    
            print("Deleted existing project:" + PROJ_NAME)
            print(f"\nMaking new project: {PROJ_NAME}")

for db_file in db_files:
    db_name = db_file.replace(".7z", "")
    
    # if '3.9.1' in db_file:
    #     assert bi.__version__ == "0.8.8", "bw2io version must be 0.8.8 for ecoinvent 3.9.1"
    
    bd.projects.set_current(PROJ_NAME)
    bi.bw2setup()

    tmp = "/tmp/"+db_name
    if not os.path.isdir(tmp):
        print("\nExtracting database...")
        with SevenZipFile(db_dir+db_file, 'r') as archive:
            archive.extractall(path=tmp)

    print("bw2io version = ", bi.__version__) #0.8.8 for ei3.9, 0.8.7 for ei3.8
    print("bw2db version = ", bd.__version__)

    path = tmp + "/datasets/"

    db = bi.SingleOutputEcospold2Importer(path, db_name)

    bi.create_core_migrations()
    db.apply_strategies()
    db.statistics()

    if db.statistics()[2] == 0:
        print("ok")
        db.write_database()
        db = bd.Database(db_name)
        db.metadata
    else:
        print("There are unlinked exchanges. Quitting.")
        
        # db.write_excel()
        #db.drop_unlinked(i_am_reckless=True)

        # db.write_database()
        # db = bd.Database(db_name)
        # db.metadata

if report:
    # bd.projects.report()
    for p in bd.projects:
        print("\n\n**** PROJECT:" + p.name)
        bd.projects.set_current(p.name)
        for d in bd.databases:
            d = bd.Database(d)
            print("\n** DB:" + d.name)
            for k, v in d.metadata.items():
                print(k , ":" , v)
