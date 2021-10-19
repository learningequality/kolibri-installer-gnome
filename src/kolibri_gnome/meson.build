kolibri_gnome_sources = [
    'application.py',
    '__init__.py',
    'kolibri_daemon_manager.py',
    'main.py',
    'utils.py',
]

python_installation.install_sources(
    kolibri_gnome_sources,
    subdir: 'kolibri_gnome'
)

kolibri_gnome = configure_file(
    input: 'kolibri-gnome.in',
    output: 'kolibri-gnome.out',
    configuration: kolibri_app_config
)

custom_target(
    'kolibri-gnome',
    input: kolibri_gnome,
    output: 'kolibri-gnome',
    command: ['cp', '@INPUT@', '@OUTPUT@'],
    install: true,
    install_dir: bindir,
    install_mode: 'rwxr-xr-x'
)
