kolibri_gnome_launcher_sources = [
    '__init__.py',
    'application.py',
    'main.py',
]

python_installation.install_sources(
    kolibri_gnome_launcher_sources,
    subdir: 'kolibri_gnome_launcher'
)

kolibri_gnome_launcher = configure_file(
    input: 'kolibri-gnome-launcher.in',
    output: 'kolibri-gnome-launcher.out',
    configuration: kolibri_app_config
)

custom_target(
    'kolibri-gnome-launcher',
    input: kolibri_gnome_launcher,
    output: 'kolibri-gnome-launcher',
    command: ['cp', '@INPUT@', '@OUTPUT@'],
    install: true,
    install_dir: kolibri_app_libexecdir,
    install_mode: 'rwxr-xr-x'
)
