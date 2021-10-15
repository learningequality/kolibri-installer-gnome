from gi.repository import Gio
from gi.repository import GLib
from gi.repository import KolibriDaemonDBus

from kolibri_app.config import DAEMON_APPLICATION_ID
from kolibri_app.config import DAEMON_MAIN_OBJECT_PATH

from .kolibri_search_handler import LocalSearchHandler
from .kolibri_service import KolibriServiceManager


INACTIVITY_TIMEOUT_MS = 30 * 1000  # 30 seconds in milliseconds

DEFAULT_STOP_KOLIBRI_TIMEOUT_SECONDS = 60  # 1 minute in seconds


class Application(Gio.Application):
    VERSION = 1

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id=DAEMON_APPLICATION_ID,
            flags=(
                Gio.ApplicationFlags.IS_SERVICE | Gio.ApplicationFlags.ALLOW_REPLACEMENT
            ),
            inactivity_timeout=INACTIVITY_TIMEOUT_MS,
            **kwargs
        )

        self.__use_session_bus = None
        self.__use_system_bus = None

        self.add_main_option(
            "session",
            0,
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Connect to the session bus",
            None,
        )

        self.add_main_option(
            "system",
            0,
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Connect to the system bus",
            None,
        )

        self.add_main_option(
            "stop-timeout",
            0,
            GLib.OptionFlags.NONE,
            GLib.OptionArg.INT,
            "Timeout in seconds before stopping Kolibri",
            None,
        )

        self.__service_manager = KolibriServiceManager()
        self.__service_manager.init()
        self.__kolibri_search_handler = LocalSearchHandler()
        self.__kolibri_search_handler.init()

        self.__watch_changes_timeout_source = None

        self.__public_dbus_interface = KolibriDaemonDBus.MainSkeleton()

        self.__public_dbus_interface.connect(
            "handle-hold", self.__on_public_dbus_interface_handle_hold
        )

        self.__public_dbus_interface.connect(
            "handle-release", self.__on_public_dbus_interface_handle_release
        )

        self.__public_dbus_interface.connect(
            "handle-start", self.__on_public_dbus_interface_handle_start
        )

        self.__public_dbus_interface.connect(
            "handle-stop", self.__on_public_dbus_interface_handle_stop
        )

        self.__public_dbus_interface.connect(
            "handle-get-item-ids-for-search",
            self.__on_public_dbus_interface_handle_get_item_ids_for_search,
        )

        self.__public_dbus_interface.connect(
            "handle-get-metadata-for-item-ids",
            self.__on_public_dbus_interface_handle_get_metadata_for_item_ids,
        )

        self.__system_name_id = 0

        self.__hold_clients = dict()
        self.__has_hold_for_kolibri_service = False

        self.__auto_stop_timeout_source = None
        self.__stop_kolibri_timeout_source = None
        self.__stop_kolibri_timeout_interval = DEFAULT_STOP_KOLIBRI_TIMEOUT_SECONDS

    @property
    def use_session_bus(self):
        return self.__use_session_bus

    @property
    def use_system_bus(self):
        return self.__use_system_bus

    @property
    def clients_count(self):
        return len(self.__hold_clients)

    def __begin_watch_changes_timeout(self):
        if self.__watch_changes_timeout_source:
            return
        self.__watch_changes_timeout_source = GLib.timeout_add_seconds(
            1, self.__watch_changes_timeout_cb
        )

    def __cancel_watch_changes_timeout(self):
        if self.__watch_changes_timeout_source:
            GLib.source_remove(self.__watch_changes_timeout_source)
            self.__watch_changes_timeout_source = None

    def __watch_changes_timeout_cb(self):
        if self.__service_manager.pop_has_changes():
            self.__update_cached_properties()
        return GLib.SOURCE_CONTINUE

    def __update_cached_properties(self):
        self.__public_dbus_interface.props.app_key = self.__service_manager.app_key
        self.__public_dbus_interface.props.base_url = self.__service_manager.base_url
        self.__public_dbus_interface.props.kolibri_home = (
            self.__service_manager.kolibri_home
        )
        self.__public_dbus_interface.props.status = self.__service_manager.status.name
        self.__public_dbus_interface.props.version = self.VERSION

    def __on_public_dbus_interface_handle_hold(self, interface, invocation):
        self.__reset_inactivity_timeout()
        self.__hold_for_client(invocation.get_connection(), invocation.get_sender())
        interface.complete_hold(invocation)
        return True

    def __on_public_dbus_interface_handle_release(self, interface, invocation):
        self.__reset_inactivity_timeout()
        self.__release_for_client(invocation.get_sender())
        interface.complete_release(invocation)
        return True

    def __on_public_dbus_interface_handle_start(self, interface, invocation):
        self.__reset_inactivity_timeout()
        self.__service_manager.start_kolibri()
        interface.complete_start(invocation)
        return True

    def __on_public_dbus_interface_handle_stop(self, interface, invocation):
        self.__reset_inactivity_timeout()
        self.__service_manager.stop_kolibri()
        interface.complete_stop(invocation)
        return True

    def __on_public_dbus_interface_handle_get_item_ids_for_search(
        self, interface, invocation, search
    ):
        self.__reset_inactivity_timeout()
        item_ids = self.__kolibri_search_handler.get_item_ids_for_search(search)
        # Using interface.complete_get_item_ids_for_search results in
        # `TypeError: Must be string, not list`, so instead we will return a
        # Variant manually...
        result_variant = GLib.Variant.new_tuple(GLib.Variant.new_strv(item_ids))
        invocation.return_value(result_variant)
        return True

    def __on_public_dbus_interface_handle_get_metadata_for_item_ids(
        self, interface, invocation, item_ids
    ):
        self.__reset_inactivity_timeout()
        metadata_list = self.__kolibri_search_handler.get_metadata_for_item_ids(
            item_ids
        )
        result_variant = GLib.Variant(
            "aa{sv}", list(map(dict_to_vardict, metadata_list))
        )
        interface.complete_get_metadata_for_item_ids(invocation, result_variant)
        return True

    def __reset_inactivity_timeout(self):
        self.hold()
        self.release()

    def __hold_for_client(self, connection, name):
        if name in self.__hold_clients.keys():
            return

        watch_id = Gio.bus_watch_name_on_connection(
            connection,
            name,
            Gio.BusNameWatcherFlags.NONE,
            None,
            self.__on_hold_client_vanished,
        )
        self.__hold_clients[name] = watch_id

    def __release_for_client(self, name):
        try:
            watch_id = self.__hold_clients.pop(name)
        except KeyError:
            pass
        else:
            Gio.bus_unwatch_name(watch_id)

    def __on_hold_client_vanished(self, connection, name):
        self.__release_for_client(name)

    def do_dbus_register(self, connection, object_path):
        if self.use_session_bus:
            self.__public_dbus_interface.export(connection, DAEMON_MAIN_OBJECT_PATH)
        self.__begin_watch_changes_timeout()
        return True

    def do_dbus_unregister(self, connection, object_path):
        self.__public_dbus_interface.unexport_from_connection(connection)
        self.__cancel_watch_changes_timeout()
        return True

    def do_name_lost(self):
        self.quit()

    def do_handle_local_options(self, options):
        use_system_bus = options.lookup_value("system", None)
        if use_system_bus is not None:
            self.__use_system_bus = use_system_bus.get_boolean()
        else:
            self.__use_system_bus = False

        use_session_bus = options.lookup_value("session", None)
        if use_session_bus is not None:
            self.__use_session_bus = use_session_bus.get_boolean()
        elif self.__use_system_bus:
            # The --session and --system options are mutually exclusive
            self.__use_session_bus = False
        else:
            self.__use_session_bus = True

        stop_timeout = options.lookup_value("stop-timeout", GLib.VariantType("i"))
        if stop_timeout is None:
            self.__stop_kolibri_timeout_interval = DEFAULT_STOP_KOLIBRI_TIMEOUT_SECONDS
        else:
            self.__stop_kolibri_timeout_interval = stop_timeout.get_int32()

        return -1

    def do_startup(self):
        if self.use_system_bus:
            Gio.bus_get(Gio.BusType.SYSTEM, None, self.__system_bus_on_get)
        self.__begin_auto_stop_timeout()
        Gio.Application.do_startup(self)

    def do_shutdown(self):
        if self.__system_name_id:
            Gio.bus_unown_name(self.__system_name_id)
            self.__system_name_id = 0

        self.__cancel_auto_stop_timeout()
        self.__kolibri_search_handler.stop()
        self.__service_manager.stop_kolibri()
        self.__service_manager.join()
        Gio.Application.do_shutdown(self)

    def __system_bus_on_get(self, source, result):
        connection = Gio.bus_get_finish(result)
        self.__public_dbus_interface.export(connection, DAEMON_MAIN_OBJECT_PATH)
        self.__system_name_id = Gio.bus_own_name_on_connection(
            connection,
            DAEMON_APPLICATION_ID,
            Gio.BusNameOwnerFlags.NONE,
            self.__on_system_name_acquired,
            self.__on_system_name_lost,
        )

    def __on_system_name_acquired(self, connection, name):
        pass

    def __on_system_name_lost(self, connection, name):
        self.__public_dbus_interface.unexport_from_connection(connection)

    def __create_kolibri_daemon(self):
        return KolibriDaemonPublicServer(
            self, self.__service_manager, self.__kolibri_search_handler
        )

    def __hold_for_kolibri_service(self):
        if not self.__has_hold_for_kolibri_service:
            self.__has_hold_for_kolibri_service = True
            self.hold()

    def __release_for_kolibri_service(self):
        if self.__has_hold_for_kolibri_service:
            self.__has_hold_for_kolibri_service = False
            self.release()

    def __begin_auto_stop_timeout(self):
        if self.__auto_stop_timeout_source:
            return
        self.__auto_stop_timeout_source = GLib.timeout_add_seconds(
            5, self.__auto_stop_timeout_cb
        )

    def __cancel_auto_stop_timeout(self):
        if self.__auto_stop_timeout_source:
            GLib.source_remove(self.__auto_stop_timeout_source)
            self.__auto_stop_timeout_source = None

    def __auto_stop_timeout_cb(self):
        # We manage Kolibri separately from GApplication's built in lifecycle
        # code. This allows us to stop the Kolibri service while providing the
        # KolibriDaemon dbus interface, instead of stopping Kolibri after the
        # dbus connection has been closed.

        self.__service_manager.cleanup()

        # Stop Kolibri if no clients are connected
        if self.clients_count == 0 and self.__service_manager.is_running():
            self.__begin_stop_kolibri_timeout()
        else:
            self.__cancel_stop_kolibri_timeout()

        # Add a GApplication hold if clients are connected or Kolibri is running
        if self.clients_count > 0 or self.__service_manager.is_running():
            self.__hold_for_kolibri_service()
        else:
            self.__release_for_kolibri_service()

        return GLib.SOURCE_CONTINUE

    def __begin_stop_kolibri_timeout(self):
        if self.__stop_kolibri_timeout_source:
            return
        self.__stop_kolibri_timeout_source = GLib.timeout_add_seconds(
            self.__stop_kolibri_timeout_interval, self.__stop_kolibri_timeout_cb
        )

    def __cancel_stop_kolibri_timeout(self):
        if self.__stop_kolibri_timeout_source:
            GLib.source_remove(self.__stop_kolibri_timeout_source)
            self.__stop_kolibri_timeout_source = None

    def __stop_kolibri_timeout_cb(self):
        if self.clients_count == 0:
            self.__service_manager.stop_kolibri()
        self.__stop_kolibri_timeout_source = None
        return GLib.SOURCE_REMOVE
