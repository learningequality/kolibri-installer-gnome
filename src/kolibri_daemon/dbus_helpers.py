from __future__ import annotations

from concurrent.futures import Future

from gi.repository import Gio
from gi.repository import GLib

from .utils import async_init_result_to_future
from .utils import async_result_to_future


class DBusManagerProxy(Gio.DBusProxy):
    @classmethod
    def get_default(cls, connection: Gio.DBusConnection):
        return cls(
            g_connection=connection,
            g_name="org.freedesktop.DBus",
            g_object_path="/org/freedesktop/DBus",
            g_interface_name="org.freedesktop.DBus",
        )

    def init_future(self):
        future = Future()
        self.init_async(
            GLib.PRIORITY_DEFAULT, None, async_init_result_to_future, future
        )
        return future

    def get_user_id_from_dbus_invocation_future(
        self, invocation: Gio.DBusMethodInvocation
    ) -> Future:
        future = Future()
        self.GetConnectionUnixUser(
            "(s)",
            invocation.get_sender(),
            result_handler=async_result_to_future,
            user_data=future,
        )
        return future
