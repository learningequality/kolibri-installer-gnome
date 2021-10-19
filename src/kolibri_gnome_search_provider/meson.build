common_dependencies = [
    gio_dep,
    gio_unix_dep,
    glib_dep,
    gobject_dep
]

shell_search_provider_dbus_src = gnome.gdbus_codegen(
    'shell-search-provider-dbus',
    sources: 'org.gnome.Shell.SearchProvider2.xml',
    interface_prefix: 'org.gnome.',
    autocleanup: 'all'
)

shell_search_provider_dbus_lib = static_library(
    'shell-search-provider-dbus',
    sources: shell_search_provider_dbus_src,
    dependencies: [common_dependencies]
)

shell_search_provider_dbus_dep = declare_dependency(
    sources: shell_search_provider_dbus_src[1],
    dependencies: common_dependencies,
    link_with: shell_search_provider_dbus_lib
)

executable(
    'kolibri-gnome-search-provider',
    sources: [
        'kolibri-gnome-search-provider.c',
        'kolibri-gnome-search-provider-application.c',
        'kolibri-gnome-search-provider-main.c',
        'kolibri-task-multiplexer.c',
        'kolibri-utils.c'
    ],
    dependencies: [
        c_config_dep,
        shell_search_provider_dbus_dep,
        kolibri_daemon_dbus_dep
    ],
    install: true,
    install_dir: kolibri_app_libexecdir
)
