#!/usr/bin/env python3

import json
import logging

from pyremarkable import RMClient

with open("private.json") as f:
    private_data = json.load(f)

token = private_data["remarkable_token"]

client = RMClient(token)

objs = client.list_objects(downloadable=True)
print(json.dumps(objs, indent=2, sort_keys=True))

if client.token != private_data["remarkable_token"]:
    logging.info("Updating private.json with the new remarkable token")
    with open("private.json","w") as f:
        private_data["remarkable_token"] = client.token
        json.dump(private_data, f, indent=4, sort_keys=True)
