#!/usr/bin/env python3

import base64
import json
import logging
import requests
from urllib.parse import urlencode
import uuid

def get_device_id_from_token(token):
    parts = token.split(".")
    parts = [p+"="*(len(p)%4) for p in parts]
    claims_data = json.loads(base64.b64decode(parts[1]).decode("utf-8"))
    return claims_data["device-id"]

class RMClient(object):
    AUTH_ENDPOINT = "https://my.remarkable.com"
    DISCOVERY_ENDPOINT = "https://service-manager-production-dot-remarkable-production.appspot.com"

    def __init__(self, token=None):
        self.token = token
        self.device_id = get_device_id_from_token(token) if token else None
        pass

    def _get(self, *args, **kwargs):
        return self._request(requests.get, *args, **kwargs)

    def _post(self, *args, **kwargs):
        return self._request(requests.post, *args, **kwargs)

    def _put(self, *args, **kwargs):
        return self._request(requests.put, *args, **kwargs)

    def _request(self, method, *args, **kwargs):
        should_retry_401 = True
        if "should_retry_401" in kwargs:
            should_retry_401 = kwargs["should_retry_401"]
            del kwargs["should_retry_401"]
        headers = {"Authorization":"Bearer {token}".format(token=self.token)} if self.token else {}
        headers.update(kwargs.get("headers",{}))
        kwargs["headers"] = headers
        if "data" in kwargs:
            if isinstance(kwargs["data"], (list,dict)):
                kwargs["data"] = json.dumps(kwargs["data"])
        r = method(*args, **kwargs)
        if r.status_code == 401 and should_retry_401:
            self.refresh_token()
            kwargs["should_retry_401"] = False
            return self._request(method, *args, **kwargs)
        if r.status_code != 200:
            raise RuntimeError("Something went wrong: HTTP{} {}".format(r.status_code, r.text))
        return r

    def get_device_token(self, code, device_id=None, device_description="desktop-windows"):
        endpoint = self.AUTH_ENDPOINT + "/token/device/new"
        device_id = device_id if device_id else str(uuid.uuid4())
        data = {"code": code, "deviceDesc": device_description, "deviceID": device_id}
        r = self._post(endpoint, data=data)
        self.token = r.text

    def refresh_token(self):
        endpoint = self.AUTH_ENDPOINT + "/token/user/new"
        r = self._post(requests.post, endpoint, data={})
        self.token = r.text
        logging.info("Token refreshed to {}".format(self.token))
        return self.token

    def _get_service_endpoint(self, service="document-storage", path=""):
        endpoint = "https://service-manager-production-dot-remarkable-production.appspot.com/service/json/1/{service}?environment=production&group=auth0%7C5a68dc51cb30df3877a1d7c4&apiVer=2".format(service=service)
        r = self._get(endpoint)
        return "https://" + r.json()["Host"] + path

    def list_objects(self, doc=None, downloadable=False):
        endpoint = self._get_service_endpoint(path="/document-storage/json/2/docs")
        params = {}
        if doc:
            params["doc"] = doc
        if downloadable:
            params["withBlob"] = True
        if params:
            endpoint += "?" + urlencode(params)
        r = self._get(endpoint)
        return r.json()

    def download_object(self, doc=None, link=None):
        if not doc and not link:
            raise RuntimeError("Either doc or link must be provided!")
        elif doc and link:
            # Yes, I realize this is janky as shit and likely to break given the slightest format change, but it works for now.
            choppable_link = link.replace("?","/").replace("&","/").lower()
            link_parts = choppable_link.split("/")
            if doc.lower() not in link_parts:
                raise RuntimeError("The link provided does not correspond to the doc provided.")
        elif doc:
            objects = self.list_objects(doc=doc, downloadable=True)
            if not objects:
                raise RuntimeError("The requested document cannot be found.")
            link = objects[0]["BlobURLGet"]
        r = self._get(link)
        # TODO: parse that shit http://remarkablewiki.com/tech/filesystem
        pass

    # Implement the rest of the stuff discussed in https://github.com/splitbrain/ReMarkableAPI/wiki/Storage
