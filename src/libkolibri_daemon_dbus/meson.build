common_dependencies = [
    gio_dep,
    gio_unix_dep,
    glib_dep,
    gobject_dep
]

kolibri_daemon_dbus_src = gnome.gdbus_codegen(
    'kolibri-daemon-dbus',
    sources: 'org.learningequality.Kolibri.Daemon.xml',
    interface_prefix: 'org.learningequality.Kolibri.',
    namespace: 'Kolibri',
    autocleanup: 'all'
)

kolibri_daemon_dbus_utils_src = [
    'kolibri-daemon-dbus-utils.c',
    'kolibri-daemon-dbus-utils.h'
]

kolibri_daemon_dbus_lib = shared_library(
    'kolibri-daemon-dbus',
    sources: [
        kolibri_daemon_dbus_src,
        kolibri_daemon_dbus_utils_src
    ],
    dependencies: [
        c_config_dep,
        common_dependencies
    ],
    install: true
)

kolibri_daemon_dbus_dep = declare_dependency(
    sources: [
        kolibri_daemon_dbus_src[1],
        kolibri_daemon_dbus_utils_src[1]
    ],
    dependencies: [common_dependencies],
    link_with: kolibri_daemon_dbus_lib,
    include_directories: '.',
)

kolibri_daemon_dbus_gir = gnome.generate_gir(
    kolibri_daemon_dbus_lib,
    sources: [
        kolibri_daemon_dbus_src,
        kolibri_daemon_dbus_utils_src
    ],
    namespace: 'KolibriDaemonDBus',
    identifier_prefix: 'KolibriDaemon',
    symbol_prefix: 'kolibri_daemon',
    nsversion: '1.0',
    includes: ['Gio-2.0'],
    dependencies: [common_dependencies],
    extra_args: ['--quiet', '--warn-all'],
    install: true
)
