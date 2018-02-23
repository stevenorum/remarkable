#!/usr/bin/env python3

import base64
import binascii
import hashlib
import json
import requests
import uuid



def call_or_throw(method, *args, **kwargs):
    r = method(*args, **kwargs)
    if r.status_code != 200:
        raise RuntimeError("Something went wrong: HTTP{} {}".format(r.status_code, r.text))
    print(r.text)
    return r

def headers(token):
    # return {"WWW-Authenticate":"Bearer {}".format(token)}
    return {"Authorization":"Bearer {}".format(token)}

def create_device_token(code, deviceDesc="desktop-windows", deviceID=None):
    deviceID = deviceID if deviceID else str(uuid.uuid4())
    data = {"code": code, "deviceDesc": deviceDesc, "deviceID": deviceID}
    print("Device ID: " + data["deviceID"])
    endpoint = "https://my.remarkable.com/token/device/new"
    r = call_or_throw(requests.post, endpoint, data=json.dumps(data), headers={"Authorization":"Bearer "})
    return deviceID, r.text

# def create_user_token(code, deviceDesc="desktop-windows", deviceID=None):
def create_user_token(code=None):
    # deviceID = deviceID if deviceID else str(uuid.uuid4())
    # data = {"code": code, "deviceDesc": deviceDesc, "deviceID": deviceID}
    # print("Device ID: " + data["deviceID"])
    data = {}
    endpoint = "https://my.remarkable.com/token/user/new"
    r = call_or_throw(requests.post, endpoint, data=json.dumps(data), headers={"Authorization":"Bearer "})
    return r.text

def refresh_device_token(token):
    # not yet working
    endpoint = "https://my.remarkable.com/token/user/new"
    data = {}
    r = call_or_throw(requests.post, endpoint, data=json.dumps(data), headers=headers(token))
    # r = call_or_throw(requests.post, endpoint, auth=JWTAuth(token))
    return r.text

def get_service_endpoint(service="document-storage"):
    endpoint = "https://service-manager-production-dot-remarkable-production.appspot.com/service/json/1/{service}?environment=production&group=auth0%7C5a68dc51cb30df3877a1d7c4&apiVer=2".format(service=service)
    r = call_or_throw(requests.get, endpoint, headers=headers(token))
    return "https://" + r.json()["Host"]

def list_objects(token):
    endpoint = "{}/document-storage/json/2/docs".format(get_service_endpoint())
    r = call_or_throw(requests.get, endpoint, headers=headers(token))
    # r = call_or_throw(requests.get, endpoint, headers=headers(token))
    return r.text

def unpack_jwt(token):
    parts = token.split(".")
    parts = [p+"="*(len(p)%4) for p in parts]
    # parts[1] = parts[1] + "="*(len(parts[1])%4)
    jose_header = base64.b64decode(parts[0]).encode("utf-8")
    print(jose_header)
    claims_set = base64.b64decode(parts[1]).encode("utf-8")
    print(claims_set)
    signature = binascii.hexlify(base64.b64decode(parts[2])).encode("utf-8")
    print(signature)
    hashlib.sha224(b"Nobody inspects the spammish repetition").hexdigest()



# print(refresh_device_token(token))
# exit(0)


# new_token = refresh_device_token(device_token)
# print(new_token)
# print(get_storage_endpoint(device_token))
# code = "wzxpyzgu"
# device_id, token = create_device_token(code)
# print("Device ID: " + device_id)
# print("Token: " + token)
# token = refresh_device_token(token)


# token = refresh_device_token(token)
# print("New token: " + token)
#print(json.dumps(json.loads(list_objects(token)), indent=2, sort_keys=True))
