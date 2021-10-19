kolibri_daemon_sources = [
    'application.py',
    'content_extensions.py',
    '__init__.py',
    'kolibri_search_handler.py',
    'kolibri_service_main.py',
    'kolibri_service.py',
    'kolibri_service_setup.py',
    'kolibri_service_stop.py',
    'main.py',
    'utils.py',
]

python_installation.install_sources(
    kolibri_daemon_sources,
    subdir: 'kolibri_daemon'
)

kolibri_daemon = executable(
    'kolibri-daemon',
    sources: ['kolibri-daemon.c'],
    dependencies: [c_config_dep, glib_dep],
    install: true,
    install_dir: kolibri_app_libexecdir,
    install_mode: 'rwxr-xr-x'
)
