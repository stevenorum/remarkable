#!/usr/bin/env python3

import dropbox
import json

with open("private.json") as f:
    private_data = json.load(f)
token = private_data["token"]
dbx = dropbox.Dropbox(token)
