#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 19:30:22 2022

@author: stew
"""

import pandas as pd
import os


path = os.getcwd() + "WasteSearchResults"

files = [x for x in os.listdir(path) if ".csv" in x]

files_tot = [x for x in files if "total" in x]



col_names = ["ex_code", "ex_name" , "ex_loc" , "ex_amount", "ex_unit" , "db_name", "category"]
results = pd.DataFrame(columns=col_names)

for file in files:
    
    result = pd.read_csv((path +"/"+ file), sep=";", header=None)
    col_names = ["ex_code", "ex_name" , "ex_loc" , "ex_amount", "ex_unit" , "db_name"]
    result = result.set_axis(col_names, axis=1)
    result.insert(0, "category", file.split("_")[1])
    results = pd.concat([results, result])



results.columns.names = col_names

unique = results.drop_duplicates(subset=['ex_name'])




#print("cutoff 38: {}, cutoff38: {} -- {}".format(len(unique), len(unique)))
