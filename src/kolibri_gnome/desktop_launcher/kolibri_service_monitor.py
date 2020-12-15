# TODO: Do we still need this if we only start polling after Kolibri starts?

import logging

logger = logging.getLogger(__name__)

import collections
import json
import threading
import time

from urllib.error import URLError
from urllib.parse import urlencode
from urllib.parse import urljoin
from urllib.parse import urlsplit
from urllib.parse import urlunsplit
from urllib.request import Request
from urllib.request import urlopen


class KolibriServiceMonitorProcess(threading.Thread):
    """
    Polls Kolibri at the expected URL to detect when it is responding to
    requests.
    - Sets context.is_responding to True when Kolibri is responding to
      requests, or to False if Kolibri fails to start.
    """

    def __init__(self, context):
        self.__context = context
        super().__init__()

    def run(self):
        base_url = self.__context.await_base_url()

        self.__context.await_is_starting()

        while not is_kolibri_responding(base_url):
            if self.__context.is_stopped:
                logger.warning("Kolibri service has died")
                self.__context.is_responding = False
                return
            time.sleep(1)

        logger.info("Kolibri service is responding")
        self.__context.is_responding = True


class KolibriAPIError(Exception):
    pass


def is_kolibri_responding(base_url):
    # Check if Kolibri is responding to http requests at the expected URL.
    try:
        info = kolibri_api_get_json(base_url, "api/public/info")
    except KolibriAPIError:
        return False
    else:
        if isinstance(info, collections.Mapping):
            return info.get("application") == "kolibri"
        else:
            return False


def kolibri_api_get_json(base_url, path, query={}):
    base_url = urlsplit(base_url)
    path = urljoin(base_url.path, path.lstrip("/"))
    request_url = base_url._replace(path=path, query=urlencode(query))
    request = Request(urlunsplit(request_url))

    try:
        response = urlopen(request)
    except URLError as error:
        raise KolibriAPIError(error)

    try:
        data = json.load(response)
    except json.JSONDecodeError as error:
        raise KolibriAPIError(error)

    return data

