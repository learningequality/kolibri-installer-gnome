import logging

logger = logging.getLogger(__name__)

import multiprocessing

from ctypes import c_bool, c_char, c_int
from enum import Enum

from .kolibri_service_main import KolibriServiceMainProcess
from .kolibri_service_setup import KolibriServiceSetupProcess
from .kolibri_service_stop import KolibriServiceStopProcess
from .utils import kolibri_update_from_home_template


class KolibriServiceContext(object):
    """
    Common context passed to KolibriService processes. This includes events
    and shared values to facilitate communication.
    """

    APP_KEY_LENGTH = 32
    BASE_URL_LENGTH = 1024
    KOLIBRI_HOME_LENGTH = 4096

    class SetupResult(Enum):
        NONE = 1
        SUCCESS = 2
        ERROR = 3

    class StartResult(Enum):
        NONE = 1
        SUCCESS = 2
        ERROR = 3

    def __init__(self):
        self.__changed_event = multiprocessing.Event()

        self.__is_starting_value = multiprocessing.Value(c_bool)
        self.__is_starting_set_event = multiprocessing.Event()

        self.__is_started_value = multiprocessing.Value(c_bool)
        self.__is_started_set_event = multiprocessing.Event()

        self.__start_result_value = multiprocessing.Value(c_int)
        self.__start_result_set_event = multiprocessing.Event()

        self.__is_stopped_value = multiprocessing.Value(c_bool)
        self.__is_stopped_set_event = multiprocessing.Event()

        self.__setup_result_value = multiprocessing.Value(c_int)
        self.__setup_result_set_event = multiprocessing.Event()

        self.__app_key_value = multiprocessing.Array(c_char, self.APP_KEY_LENGTH)
        self.__app_key_set_event = multiprocessing.Event()

        self.__base_url_value = multiprocessing.Array(c_char, self.BASE_URL_LENGTH)
        self.__base_url_set_event = multiprocessing.Event()

        self.__kolibri_home_value = multiprocessing.Array(
            c_char, self.KOLIBRI_HOME_LENGTH
        )
        self.__kolibri_home_set_event = multiprocessing.Event()

    def push_has_changes(self):
        self.__changed_event.set()

    def pop_has_changes(self):
        # TODO: It would be better to use a multiprocessing.Condition and wait()
        #       on it, but this does not play nicely with GLib's main loop.
        if self.__changed_event.is_set():
            self.__changed_event.clear()
            return True
        else:
            return False

    @property
    def is_starting(self):
        if self.__is_starting_set_event.is_set():
            return self.__is_starting_value.value
        else:
            return None

    @is_starting.setter
    def is_starting(self, is_starting):
        if is_starting is None:
            self.__is_starting_set_event.clear()
            self.__is_starting_value.value = False
        else:
            self.__is_starting_value.value = bool(is_starting)
            self.__is_starting_set_event.set()
        self.push_has_changes()

    def await_is_starting(self):
        self.__is_starting_set_event.wait()
        return self.is_starting

    @property
    def is_started(self):
        if self.__is_started_set_event.is_set():
            return self.__is_started_value.value
        else:
            return None

    @is_started.setter
    def is_started(self, is_started):
        if is_started is None:
            self.__is_started_set_event.clear()
            self.__is_started_value.value = False
        else:
            self.__is_started_value.value = bool(is_started)
            self.__is_started_set_event.set()
        self.push_has_changes()

    def await_is_started(self):
        self.__is_started_set_event.wait()
        return self.is_started

    @property
    def start_result(self):
        if self.__start_result_set_event.is_set():
            return self.StartResult(self.__start_result_value.value)
        else:
            return None

    @start_result.setter
    def start_result(self, start_result):
        if start_result is None:
            self.__start_result_set_event.clear()
            self.__start_result_value.value = 0
        else:
            self.__start_result_value.value = start_result.value
            self.__start_result_set_event.set()
        self.push_has_changes()

    def await_start_result(self):
        self.__start_result_set_event.wait()
        return self.start_result

    @property
    def is_stopped(self):
        if self.__is_stopped_set_event.is_set():
            return self.__is_stopped_value.value
        else:
            return None

    @is_stopped.setter
    def is_stopped(self, is_stopped):
        self.__is_stopped_value.value = is_stopped
        if is_stopped is None:
            self.__is_stopped_set_event.clear()
        else:
            self.__is_stopped_set_event.set()
        self.push_has_changes()

    def await_is_stopped(self):
        self.__is_stopped_set_event.wait()
        return self.is_stopped

    @property
    def setup_result(self):
        if self.__setup_result_set_event.is_set():
            return self.SetupResult(self.__setup_result_value.value)
        else:
            return None

    @setup_result.setter
    def setup_result(self, setup_result):
        if setup_result is None:
            self.__setup_result_set_event.clear()
            self.__setup_result_value.value = 0
        else:
            self.__setup_result_value.value = setup_result.value
            self.__setup_result_set_event.set()
        self.push_has_changes()

    def await_setup_result(self):
        self.__setup_result_set_event.wait()
        return self.setup_result

    @property
    def app_key(self):
        if self.__app_key_set_event.is_set():
            return self.__app_key_value.value.decode("ascii")
        else:
            return None

    @app_key.setter
    def app_key(self, app_key):
        self.__app_key_value.value = bytes(app_key, encoding="ascii")
        if app_key is None:
            self.__app_key_set_event.clear()
        else:
            self.__app_key_set_event.set()
        self.push_has_changes()

    def await_app_key(self):
        self.__app_key_set_event.wait()
        return self.app_key

    @property
    def base_url(self):
        if self.__base_url_set_event.is_set():
            return self.__base_url_value.value.decode("ascii")
        else:
            return None

    @base_url.setter
    def base_url(self, base_url):
        self.__base_url_value.value = bytes(base_url, encoding="ascii")
        if base_url is None:
            self.__base_url_set_event.clear()
        else:
            self.__base_url_set_event.set()
        self.push_has_changes()

    def await_base_url(self):
        self.__base_url_set_event.wait()
        return self.base_url

    @property
    def kolibri_home(self):
        if self.__kolibri_home_set_event.is_set():
            return self.__kolibri_home_value.value.decode("ascii")
        else:
            return None

    @kolibri_home.setter
    def kolibri_home(self, kolibri_home):
        self.__kolibri_home_value.value = bytes(kolibri_home, encoding="ascii")
        if kolibri_home is None:
            self.__kolibri_home_set_event.clear()
        else:
            self.__kolibri_home_set_event.set()
        self.push_has_changes()

    def await_kolibri_home(self):
        self.__kolibri_home_set_event.wait()
        return self.kolibri_home


class KolibriServiceManager(KolibriServiceContext):
    """
    Manages the Kolibri service, starting and stopping it in separate
    processes, and checking for availability.
    """

    class Status(Enum):
        NONE = 1
        STARTING = 2
        STOPPED = 3
        STARTED = 4
        ERROR = 5

    def __init__(self):
        super().__init__()

        self.is_stopped = True

        self.__main_process = None
        self.__setup_process = None
        self.__stop_process = None

    def init(self):
        kolibri_update_from_home_template()

    @property
    def status(self):
        if self.is_starting:
            return self.Status.STARTING
        elif self.start_result == self.StartResult.SUCCESS:
            return self.Status.STARTED
        elif self.start_result == self.StartResult.ERROR:
            return self.Status.ERROR
        elif self.setup_result == self.SetupResult.ERROR:
            return self.Status.ERROR
        elif self.is_stopped:
            return self.Status.STOPPED
        else:
            return self.Status.NONE

    def is_running(self):
        return self.status in [self.Status.STARTING, self.Status.STARTED]

    def get_kolibri_url(self, **kwargs):
        from urllib.parse import urljoin
        from urllib.parse import urlsplit
        from urllib.parse import urlunsplit

        base_url = self.await_base_url()

        base_url = urlsplit(base_url)
        if "path" in kwargs:
            kwargs["path"] = urljoin(base_url.path, kwargs["path"].lstrip("/"))
        target_url = base_url._replace(**kwargs)
        return urlunsplit(target_url)

    def join(self):
        if self.__setup_process and self.__setup_process.is_alive():
            self.__setup_process.join()
        if self.__main_process and self.__main_process.is_alive():
            self.__main_process.join()
        if self.__stop_process and self.__stop_process.is_alive():
            self.__stop_process.join()

    def cleanup(self):
        # Clean up finished processes to keep things tidy, without blocking.
        if self.__setup_process and not self.__setup_process.is_alive():
            self.__setup_process = None
        if self.__main_process and not self.__main_process.is_alive():
            self.__main_process = None
        if self.__stop_process and not self.__stop_process.is_alive():
            self.__stop_process = None

    def watch_changes(self, callback):
        watch_changes_thread = WatchChangesThread(self, callback)
        watch_changes_thread.start()

    def start_kolibri(self):
        if self.__main_process and self.__main_process.is_alive():
            return

        if not self.__setup_process:
            self.__setup_process = KolibriServiceSetupProcess(self)
            self.__setup_process.start()

        self.__main_process = KolibriServiceMainProcess(self)
        self.__main_process.start()

    def stop_kolibri(self):
        if not self.is_running():
            return
        elif self.__stop_process and self.__stop_process.is_alive():
            return
        else:
            self.__stop_process = KolibriServiceStopProcess(self)
            self.__stop_process.start()

    def pop_has_changes(self):
        # The main process might exit prematurely. If that happens, we should
        # set is_stopped accordingly.
        if (
            self.__main_process
            and not self.__main_process.is_alive()
            and not self.is_stopped
        ):
            self.is_starting = False
            if self.start_result != self.StartResult.ERROR:
                self.start_result = None
            self.is_stopped = True
            self.base_url = ""
            self.app_key = ""
        return super().pop_has_changes()
