from __future__ import annotations

import os
import pwd
import typing
from concurrent.futures import Future

from gi.repository import Gio
from gi.repository import GLib

from .utils import async_init_result_to_future
from .utils import async_result_to_future
from .utils import future_chain


LOCAL_USER = os.environ.get("USER", None)

try:
    LOCAL_USER_PWD = pwd.getpwnam(LOCAL_USER)
except KeyError:
    LOCAL_USER_PWD = None


class UserInfo(typing.NamedTuple):
    user_id: int
    user_name: str
    full_name: str
    is_admin: bool

    @classmethod
    def from_accounts_service_user(
        cls, user: AccountsServiceUser, **kwargs
    ) -> UserInfo:
        return cls(
            user_id=user.user_id,
            user_name=user.user_name,
            full_name=user.full_name,
            is_admin=user.is_admin,
            **kwargs
        )

    @classmethod
    def from_pwd_user(cls, user: pwd.struct_passwd, **kwargs) -> UserInfo:
        return cls(
            user_id=user.pw_uid,
            user_name=user.pw_name,
            full_name=user.pw_gecos,
            **kwargs
        )

    @classmethod
    def from_user_id_future(
        cls, user_id: str, accounts_service: AccountsServiceManager = None
    ) -> Future:
        out_future = Future()

        if LOCAL_USER_PWD and user_id == LOCAL_USER_PWD.pw_uid:
            user_info = UserInfo.from_pwd_user(LOCAL_USER_PWD, is_admin=True)
            out_future.set_result(user_info)
        elif accounts_service:
            future_chain(
                accounts_service.get_user_by_id_future(user_id),
                out_future,
                map_fn=cls.from_accounts_service_user,
            )
        else:
            out_future.set_exception(Exception("Unknown user"))

        return out_future


class AccountsServiceManager(Gio.DBusProxy):
    """
    This is a rough copy of what we need from libaccountsservice to get basic
    information about desktop users. It would be nice to use that library, but
    it is not available in the GNOME 40 flatpak runtime.
    """

    @classmethod
    def get_default(cls, connection: Gio.DBusConnection) -> AccountsServiceManager():
        return cls(
            g_connection=connection,
            g_name="org.freedesktop.Accounts",
            g_object_path="/org/freedesktop/Accounts",
            g_interface_name="org.freedesktop.Accounts",
        )

    def init_future(self):
        future = Future()
        self.init_async(
            GLib.PRIORITY_DEFAULT, None, async_init_result_to_future, future
        )
        return future

    def get_user_by_id_future(self, user_id: int) -> Future:
        user_path_future = Future()
        self.FindUserById(
            "(x)",
            user_id,
            result_handler=async_result_to_future,
            user_data=user_path_future,
        )
        return future_chain(
            future_chain(user_path_future, map_fn=self.__new_accounts_service_user),
            map_fn=AccountsServiceUser.init_future,
        )

    def __new_accounts_service_user(self, object_path: str):
        return AccountsServiceUser.new_with_object_path(self, object_path)


class AccountsServiceUser(Gio.DBusProxy):
    ACCOUNT_TYPE_ADMIN = 1

    @classmethod
    def new_with_object_path(
        cls, manager: AccountsServiceManager, path: str
    ) -> AccountsServiceUser():
        return cls(
            g_connection=manager.get_connection(),
            g_name=manager.get_name(),
            g_object_path=path,
            g_interface_name="org.freedesktop.Accounts.User",
        )

    def init_future(self):
        future = Future()
        self.init_async(
            GLib.PRIORITY_DEFAULT, None, async_init_result_to_future, future
        )
        return future

    @property
    def user_id(self) -> int:
        return self.__unpack_property("Uid")

    @property
    def user_name(self) -> str:
        return self.__unpack_property("UserName")

    @property
    def full_name(self) -> str:
        return self.__unpack_property("RealName")

    @property
    def is_admin(self) -> bool:
        return self.__unpack_property("AccountType") == self.ACCOUNT_TYPE_ADMIN

    def __unpack_property(self, name: str) -> typing.Any:
        result = self.get_cached_property(name)
        if result is None:
            return None
        else:
            return result.unpack()
