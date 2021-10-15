import logging

logger = logging.getLogger(__name__)

import gettext
import importlib.util
import os

from pathlib import Path

from . import config

if config.BUILD_PROFILE == "development":
    profile_environ_prefix = "KOLIBRI_DEVEL_"
else:
    profile_environ_prefix = "KOLIBRI_"

KOLIBRI_APP_DEVELOPER_EXTRAS = os.environ.get(
    profile_environ_prefix + "APP_DEVELOPER_EXTRAS"
)

XDG_CURRENT_DESKTOP = os.environ.get("XDG_CURRENT_DESKTOP")

# Logic for KOLIBRI_HOME is from kolibri.utils.conf. We avoid importing it from
# Kolibri because the import comes with side-effects.
DEFAULT_KOLIBRI_HOME_PATH = Path.home().joinpath(".kolibri")
if "KOLIBRI_HOME" in os.environ:
    KOLIBRI_HOME_PATH = Path(os.environ["KOLIBRI_HOME"]).expanduser().absolute()
else:
    KOLIBRI_HOME_PATH = DEFAULT_KOLIBRI_HOME_PATH


def init_gettext():
    gettext.bindtextdomain(config.GETTEXT_PACKAGE, config.LOCALE_DIR)
    gettext.textdomain(config.GETTEXT_PACKAGE)


def init_logging(log_file_name="kolibri-app.txt", level=logging.DEBUG):
    from kolibri.utils.logger import KolibriTimedRotatingFileHandler

    logging.basicConfig(level=level)

    try:
        logs_dir_path = KOLIBRI_HOME_PATH.joinpath("logs")
        logs_dir_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # This is handled in the following block
        pass

    if not os.access(logs_dir_path, os.W_OK):
        logs_dir_path = DEFAULT_KOLIBRI_HOME_PATH.joinpath("logs")
        logs_dir_path.mkdir(parents=True, exist_ok=True)

    log_file_path = logs_dir_path.joinpath(log_file_name)

    root_logger = logging.getLogger()
    file_handler = KolibriTimedRotatingFileHandler(
        filename=log_file_path.as_posix(), when="midnight", backupCount=30
    )

    root_logger.addHandler(file_handler)

    return logs_dir_path


def init_kolibri():
    from kolibri.plugins.registry import registered_plugins
    from kolibri.utils.cli import initialize, setup_logging

    registered_plugins.register_plugins(["kolibri.plugins.app"])

    if importlib.util.find_spec("kolibri_app_desktop_xdg_plugin"):
        registered_plugins.register_plugins(["kolibri_app_desktop_xdg_plugin"])

    setup_logging(debug=False)
    initialize()


def get_current_language():
    try:
        translations = gettext.translation(
            config.GETTEXT_PACKAGE, localedir=config.LOCALE_DIR
        )
        locale_info = translations.info()
    except FileNotFoundError as e:
        logger.warning("Error loading translation file: %s", e)
        language = None
    else:
        language = locale_info.get("language")

    return language
