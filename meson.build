project('kolibri-gnome', ['c'],
    meson_version: '>= 0.56.0',
    version: run_command('cat', 'VERSION').stdout().strip()
)

package_string = '@0@-@1@'.format(meson.project_name(), meson.project_version())

gnome = import('gnome')
python = import('python')
i18n = import('i18n')

python_installation = python.find_installation('python3')

git_program = find_program('git', required : false, disabler : true)
git_describe_command = run_command(git_program, 'describe', '--dirty')

if git_program.found() and git_describe_command.returncode() == 0
  git_commit = git_describe_command.stdout().strip()
else
  git_commit = meson.project_version()
endif

bindir = join_paths(get_option('prefix'), get_option('bindir'))
libexecdir = join_paths(get_option('prefix'), get_option('libexecdir'))
locale_dir = join_paths(get_option('prefix'), get_option('localedir'))
datadir = join_paths(get_option('prefix'), get_option('datadir'))

build_profile = get_option('profile')
base_application_id = get_option('base_application_id')
base_object_path = get_option('base_object_path')
profile_env_prefix = get_option('env_prefix')
profile_uri_prefix = get_option('uri_prefix')

if build_profile == 'development'
    base_application_id += '.Devel'
    base_object_path += '/Devel'
    profile_env_prefix += 'DEVEL_'
    profile_uri_prefix += '-devel'
endif

frontend_application_id = base_application_id
frontend_object_path = base_object_path

frontend_channel_application_id_prefix = base_application_id + '.channel_'

launcher_application_id = base_application_id + '.Launcher'

daemon_application_id = base_application_id + '.Daemon'
daemon_object_path = base_object_path + '/Daemon'
daemon_main_object_path = daemon_object_path + '/Main'
daemon_private_object_path = daemon_object_path + '/Private'

search_provider_application_id = base_application_id + '.SearchProvider'
search_provider_object_path = base_object_path + '/SearchProvider'

kolibri_uri_scheme = 'kolibri'
app_uri_scheme = profile_uri_prefix + '-app'
dispatch_uri_scheme = profile_uri_prefix + '-dispatch'

po_dir = join_paths(meson.project_source_root(), 'po')

kolibri_app_libexecdir = join_paths(libexecdir, 'kolibri-app')
kolibri_app_data_dir = join_paths(datadir, 'kolibri-app')

kolibri_app_config = configuration_data()
kolibri_app_config.set('BINDIR', bindir)
kolibri_app_config.set('PYTHON', 'python3')
kolibri_app_config.set('PACKAGE_STRING', package_string)
kolibri_app_config.set('PROJECT_VERSION', meson.project_version())
kolibri_app_config.set('VCS_TAG', git_commit)
kolibri_app_config.set('GETTEXT_PACKAGE', meson.project_name())
kolibri_app_config.set('LOCALE_DIR', locale_dir)
kolibri_app_config.set('BUILD_PROFILE', build_profile)
kolibri_app_config.set('PROFILE_ENV_PREFIX', profile_env_prefix)
kolibri_app_config.set('KOLIBRI_URI_SCHEME', kolibri_uri_scheme)
kolibri_app_config.set('APP_URI_SCHEME', app_uri_scheme)
kolibri_app_config.set('DISPATCH_URI_SCHEME', dispatch_uri_scheme)
kolibri_app_config.set('KOLIBRI_APP_LIBEXECDIR', kolibri_app_libexecdir)
kolibri_app_config.set('KOLIBRI_APP_DATA_DIR', kolibri_app_data_dir)
kolibri_app_config.set('BASE_APPLICATION_ID', base_application_id)
kolibri_app_config.set('BASE_OBJECT_PATH', base_object_path)
kolibri_app_config.set('FRONTEND_APPLICATION_ID', frontend_application_id)
kolibri_app_config.set('LAUNCHER_APPLICATION_ID', launcher_application_id)
kolibri_app_config.set('FRONTEND_OBJECT_PATH', frontend_object_path)
kolibri_app_config.set('FRONTEND_CHANNEL_APPLICATION_ID_PREFIX', frontend_channel_application_id_prefix)
kolibri_app_config.set('DAEMON_APPLICATION_ID', daemon_application_id)
kolibri_app_config.set('DAEMON_OBJECT_PATH', daemon_object_path)
kolibri_app_config.set('DAEMON_MAIN_OBJECT_PATH', daemon_main_object_path)
kolibri_app_config.set('DAEMON_PRIVATE_OBJECT_PATH', daemon_private_object_path)
kolibri_app_config.set('SEARCH_PROVIDER_APPLICATION_ID', search_provider_application_id)
kolibri_app_config.set('SEARCH_PROVIDER_OBJECT_PATH', search_provider_object_path)

subdir('data')
subdir('po')
subdir('src')

subdir('tests')
