import json
import os

with open(os.path.join(os.getcwd(), "values\\rimeheart_giveaway.json"), "r", encoding="utf-8-sig") as f:
    data = json.load(f)

for game in data["invalid_codes"].keys():
    if game in data["valid_codes"].keys():
        del data["valid_codes"][game]
    if game in data["skipped_codes"].keys():
        del data["skipped_codes"][game]

with open("rimeheart_giveaway.json", "w", encoding="utf-8-sig") as f:
    json.dump(data, f)