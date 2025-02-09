import bw2io as bi
import os

print("bw2io version:", bi.__version__)

dir_projects = os.environ.get("HOME") + "/bw"
if not os.path.isdir(dir_projects): os.makedirs(dir_projects)

os.environ["BRIGHTWAY2_DIR"] = dir_projects
os.environ.get("BRIGHTWAY2_DIR")

# for k, v in os.environ.items():
#     print(f'{k}={v}')



bi.install_project('ecoinvent-3.8-biosphere', 'my-new-project')