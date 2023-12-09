#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 14 11:02:52 2022

@author: stew
"""


def eiWriteDB(version):

    from py7zr import SevenZipFile
    import os
    import bw2io as bi
    import bw2data as bd




    print("bw2io version = ", bi.__version__)
    print("bw2db version = ", bd.__version__)
    #eidl = "/home/stew/.local/share/EcoInventDownloader"


    bd.projects.set_current(version)


    path = "/home/stew/OneDrive/CML/DBs/"
    dbzip = "cutoff{}.7z".format(ei)
    dbname = version

    zip_file = "/home/stew/.local/share/EcoInventDownloader/") + dbname

    tmp = os.path.join(path, "tmp")
    if not os.path.isdir(tmp):
        os.mkdir(os.path.join(path+"tmp"))

    SevenZipFile(zip_file).extractall(tmp)

    db = bd.SingleOutputEcospold2Importer(os.path.join(tmp, "datasets/"), dbname)
    db.apply_strategies()
    db.statistics()
    db.write_database()

    #os.removedirs(tmp)
