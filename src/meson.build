gio_dep = dependency('gio-2.0')
gio_unix_dep = dependency('gio-unix-2.0')
glib_dep = dependency('glib-2.0')
gobject_dep = dependency('gobject-2.0')

c_config = configuration_data()
c_config.set_quoted('PYTHON', python_installation.path())
c_config.set_quoted('PACKAGE_STRING', package_string)
c_config.set_quoted('KOLIBRI_ENV_PREFIX', kolibri_env_prefix)
c_config.set_quoted('FRONTEND_APPLICATION_ID', frontend_application_id)
c_config.set_quoted('FRONTEND_OBJECT_PATH', frontend_object_path)
c_config.set_quoted('FRONTEND_CHANNEL_APPLICATION_ID_PREFIX', frontend_channel_application_id_prefix)
c_config.set_quoted('LAUNCHER_APPLICATION_ID', launcher_application_id)
c_config.set_quoted('DAEMON_APPLICATION_ID', daemon_application_id)
c_config.set_quoted('DAEMON_MAIN_OBJECT_PATH', daemon_main_object_path)
c_config.set_quoted('DAEMON_PRIVATE_OBJECT_PATH', daemon_private_object_path)
c_config.set_quoted('SEARCH_PROVIDER_APPLICATION_ID', search_provider_application_id)
c_config.set_quoted('SEARCH_PROVIDER_OBJECT_PATH', search_provider_object_path)

c_config_dep = declare_dependency(
    sources: configure_file(
        output: 'config.h',
        configuration: c_config
    ),
    include_directories: include_directories('.')
)

subdir('libkolibri_daemon_dbus')

subdir('kolibri_app')
subdir('kolibri_daemon')
subdir('kolibri_gnome')
subdir('kolibri_gnome_launcher')
subdir('kolibri_gnome_search_provider')
