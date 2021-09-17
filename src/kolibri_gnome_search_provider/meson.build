gio_dep = dependency('gio-2.0')
gio_unix_dep = dependency('gio-unix-2.0')
glib_dep = dependency('glib-2.0')
gobject_dep = dependency('gobject-2.0')

search_provider_config = configuration_data()
search_provider_config.set_quoted('PACKAGE_STRING', package_string)
search_provider_config.set_quoted('FRONTEND_APPLICATION_ID', frontend_application_id)
search_provider_config.set_quoted('FRONTEND_OBJECT_PATH', frontend_object_path)
search_provider_config.set_quoted('FRONTEND_CHANNEL_APPLICATION_ID_PREFIX', frontend_channel_application_id_prefix)
search_provider_config.set_quoted('LAUNCHER_APPLICATION_ID', launcher_application_id)
search_provider_config.set_quoted('DAEMON_APPLICATION_ID', daemon_application_id)
search_provider_config.set_quoted('DAEMON_OBJECT_PATH', daemon_object_path)
search_provider_config.set_quoted('SEARCH_PROVIDER_APPLICATION_ID', search_provider_application_id)
search_provider_config.set_quoted('SEARCH_PROVIDER_OBJECT_PATH', search_provider_object_path)

config_file = configure_file(
    output: 'config.h',
    configuration: search_provider_config
)

common_dependencies = [
    gio_dep,
    gio_unix_dep,
    glib_dep,
    gobject_dep
]

shell_search_provider_dbus_sources = gnome.gdbus_codegen(
    'shell-search-provider-dbus',
    sources: 'org.gnome.Shell.SearchProvider2.xml',
    interface_prefix: 'org.gnome.'
)

shell_search_provider_dbus_lib = static_library(
    'shell_search_provider_dbus',
    sources: shell_search_provider_dbus_sources,
    dependencies: common_dependencies,
    include_directories: include_directories('.')
)

shell_search_provider_dbus_lib_dep = declare_dependency(
    link_with: shell_search_provider_dbus_lib,
    dependencies: common_dependencies,
    include_directories: include_directories('.')
)

kolibri_daemon_dbus_sources = gnome.gdbus_codegen(
    'kolibri-daemon-dbus',
    sources: 'org.learningequality.Kolibri.Daemon.xml',
    interface_prefix: 'org.learningequality.'
)

kolibri_daemon_dbus_lib = static_library(
    'kolibri_daemon_dbus',
    sources: kolibri_daemon_dbus_sources,
    dependencies: common_dependencies,
    include_directories: include_directories('.')
)

kolibri_daemon_dbus_lib_dep = declare_dependency(
    link_with: kolibri_daemon_dbus_lib,
    dependencies: common_dependencies,
    include_directories: include_directories('.')
)

search_provider_dependencies = [
    common_dependencies,
    shell_search_provider_dbus_lib_dep,
    kolibri_daemon_dbus_lib_dep
]

executable(
    'kolibri-gnome-search-provider',
    sources: [
        'kolibri-gnome-search-provider.c',
        'kolibri-gnome-search-provider-application.c',
        'kolibri-gnome-search-provider-main.c',
        'kolibri-utils.c'
    ] + kolibri_daemon_dbus_sources + shell_search_provider_dbus_sources,
    dependencies: search_provider_dependencies,
    install: true,
    install_dir: kolibri_gnome_libexecdir
)

