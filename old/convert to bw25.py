# convert to bw25

import bw2data as bd


bd.__version__

sorted(bd.projects)

bd.projects.dir
bd.projects.report()

#%%
for p in list(bd.projects):
    if 'default' in p.name:
        print(p.name)
        bd.projects.delete_project(p.name, True)
bd.projects.report()

# %%

# 
bd.projects.purge_deleted_directories()