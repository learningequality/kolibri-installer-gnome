kolibri_app_sources = [
    'globals.py',
    '__init__.py',
    'kolibri_settings.py',
]

python_installation.install_sources(
    kolibri_app_sources,
    subdir: 'kolibri_app'
)

configure_file(
    input : 'config.py.in',
    output : 'config.py',
    configuration : kolibri_app_config,
    install_dir : join_paths(
        python_installation.get_install_dir(
            subdir: 'kolibri_app',
            pure: false
        )
    )
)