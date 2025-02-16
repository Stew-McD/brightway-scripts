#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 17:07:23 2022

@author: stew
"""
import os
import bw2io as bi
import bw2data as bd


def inspect():
    
    for p in list(bd.projects):
        print("\n", p.name)
        try:
            bd.projects.set_current(p.name)
            for DB in bd.databases:
                db = bd.Database(DB)
                print( db.metadata['number'], "entries in :\t", DB)
            
        except Exception as e:
            print(e)
            pass
        
        for d in bd.databases:
            print("\t", d)

            try:
                db = bd.Database(d)
                db.metadata
            except:
                print(d + "  ERROR")
                pass



#%% BACKUP PROJECTS
# for k, v in os.environ.items():
#     print(f'{k}={v}')
def backup():
    

    archive = os.environ.get("HOME") + "/alice"
    if not os.path.isdir(archive): os.mkdir(archive)
    os.environ["HOME"] = archive
    os.environ.get("HOME")


    for i, p in enumerate(bd.projects.report()):
        if p[1] != 0:
            if all(x not in p[0] for x in ["test", 'con']):
                print (i+1,"/",len(bd.projects),": ", p)
                print("Backup: ", p[0])
                bi.backup.backup_project_directory(p[0])

backup()
os.environ["HOME"]= "/home/stew"

#bi.restore_project_directory('/home/stew/alice/brightway2-project-default-backup.05-December-2022-05-28PM.tar.gz')

#%% DELETE: Clean up projects and databases
def delete():

    todelete = []
    for p in bd.projects.report():
        print("\n", p[0])
        bd.projects.set_current(p[0])
        for d in bd.databases:
            print("\t", d)

            try:
                db = bd.Database(d)
                db.metadata
            except:
                print(d + "  ERROR")
                todelete.append(d)
                pass

        if len(todelete) != 0 :
            for d in todelete:
                # del bd.databases[d]
                print(d + " was deleted")


    for proj in bd.projects.report():
        if proj[1] == 0:
        # if "WasteFootprint" in proj[0]:
            # bd.projects.delete_project(proj[0], delete_dir=True)
            print("Deleted: ", proj)


    for p in bd.projects.report():
        print("\n", p)

delete()



for db in list(bd.databases):
    if "2020" in db:
        del bd.databases[db]
        print(db + " was deleted")