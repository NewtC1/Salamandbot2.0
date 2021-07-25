import json
import os
import uuid
import utils.helper_functions as hf

log_data = hf.load_logs()
woodchips_data = hf.load_woodchips()

output_data = {}

for key in log_data.keys():
    output_data[str(uuid.uuid1())] = {"aliases": [key], "logs": log_data[key], "active_name": key}

for key in woodchips_data["Users"].keys():
    user_registered = False
    for id in output_data.keys():
        if key in output_data[id]["aliases"]:
            output_data[id]["woodchips"] = woodchips_data["Users"][key]
            user_registered = True

    if not user_registered:
        output_data[str(uuid.uuid1())] = woodchips_data["Users"][key]

print(os.getcwd())

with open(os.path.join(os.getcwd(), "values/accounts.json"), "w+", encoding="utf-8-sig") as file_stream:
    json.dump(output_data, file_stream, indent="\t")