import database

p = database.get_project(11)
if p:
    print("Project 11 details:")
    for k, v in dict(p).items():
        print(f"  {k}: {repr(v)}")
else:
    print("Project 11 not found.")
