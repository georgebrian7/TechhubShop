import json

with open("data.json", "r") as f:
    data = json.load(f)

# Exclude system tables
exclude_models = [
    "auth.permission",
    "contenttypes.contenttype",
    "admin.logentry",
    "sessions.session"
]

filtered = [obj for obj in data if obj["model"] not in exclude_models]

with open("clean_data.json", "w") as f:
    json.dump(filtered, f, indent=2)

print("Cleaned file saved as clean_data.json")
