import bw2data as bd

KEEP = [
    'default',
]

for project in bd.projects:
    if project not in KEEP:
        try:
            bd.projects.delete_project(project, delete_dir=True)
        except Exception as e:
            print(e)
            print(f"Failed to delete project {project}")


