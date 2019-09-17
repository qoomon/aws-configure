from os import (path, environ)
import sys
from io import StringIO
from collections import namedtuple
from argparse import ArgumentParser
from configparser import ConfigParser

from botocore.session import Session
from awscli.customizations.configure.writer import ConfigFileWriter

aws_config_path = path.expanduser(
    Session().get_config_variable('config_file'))
aws_credentials_path = path.expanduser(
    Session().get_config_variable('credentials_file'))

def argv_get(index):
    return sys.argv[index] if index < len(sys.argv) else None


def split_key_value(key_value, separator):
    key_value_split = key_value.split(separator, 1)
    if len(key_value_split) != 2:
        raise ValueError("Invalid key value '" + key_value + "' expected format '<key>" +
                         separator + "<value>', but was '" + key_value + "'")
    return namedtuple('KeyValue', ['key', 'value'])(key=key_value_split[0], value=key_value_split[1])


def profile_config_section(profile_name):
    return "profile " + profile_name if profile_name != "default" else "default"


def profile_update(config_path, profile_section, config, merge=False):

    profile_delete(config_path, profile_section, clear=(not merge))

    # add empty line as profile separator
    current_config = ConfigParser()
    current_config.read(config_path)
    if current_config.sections() and profile_section not in current_config.sections():
        with open(config_path, 'a') as config_file:
            config_file.write('\n')

    ConfigFileWriter().update_config({
        **config,
        '__section__': profile_section
    }, config_path)


def profile_delete(config_path, profile_section, clear=False):
    with open(config_path) as config_file:
        config_string = config_file.read()

    with open(config_path, 'w') as config_file:
        write = True
        for config_line in StringIO(config_string):
            section_match = ConfigFileWriter.SECTION_REGEX.search(config_line)
            if section_match is not None:
                if section_match.group('header') == profile_section:
                    if clear:
                        config_file.write(config_line)
                    write = False
                else:
                    if clear and not write:
                        config_file.write('\n')
                    write = True
            if write:
                config_file.write(config_line)


def print_help():
    print("""\
usage: 

    configure profile:

        aws-configure set [--profile/-p <profile_name>] [--clean/-c] <config_options...>
            
            --profile/-p <profile_name> : select profile to use else 'default'
            <config_options>            : key=value pairs e.g. 'region=eu-central-1' 'source_profile=default'
            --clean/-c                  : clear all profile options before setting new options (except credentials)
            
    delete profile:

        aws-configure delete --profile/-p <profile_name> [--config] [--credentials]
        
            --config      : delete only profile config in '~/.aws/config'
            --credentials : delete only profile credentials in '~/.aws/credentials'
        
    list profiles:

        aws-configure list
    
    print help
    
        aws-configure help
        
""")


def handle_list_profiles():
    profile_map = Session().full_config['profiles']
    for profile_name, profile in profile_map.items():
        print(profile_name)


def handle_delete_profile():
    sys.argv.pop(1)
    profile_name = 'default'
    if argv_get(1) in ('--profile', '-p'):
        profile_name = argv_get(2)
        sys.argv.pop(1)
        sys.argv.pop(1)
    # TODO add option to toggle
    delete_config = True
    delete_credentials = True

    if delete_config:
        profile_delete(aws_config_path, profile_config_section(profile_name))
    if delete_credentials:
        profile_delete(aws_credentials_path, profile_name)


def handle_set_profile():
    sys.argv.pop(1)
    profile_name = 'default'
    if argv_get(1) in ('--profile', '-p'):
        profile_name = argv_get(2)
        sys.argv.pop(1)
        sys.argv.pop(1)

    profile_config = {}
    profile_credentials = {}
    for option in sys.argv[1:]:
        option = split_key_value(option, '=')
        if option.key not in ['aws_access_key_id', 'aws_secret_access_key', 'aws_session_token']:
            profile_config[option.key] = option.value
        else:
            profile_credentials[option.key] = option.value

    if profile_config:
        print("set profile config")
        # TODO add option to toggle merge
        profile_update(aws_config_path, profile_config_section(profile_name),
                       profile_config, merge=False)

    if profile_credentials:
        print("set profile credentials")
        profile_update(aws_credentials_path, profile_name,
                       profile_credentials, merge=False)


def main():
    if argv_get(1) == 'help':
        print_help()
    elif argv_get(1) == 'list':
        handle_list_profiles()
    elif argv_get(1) == 'delete':
        handle_delete_profile()
    elif argv_get(1) == 'set':
        handle_set_profile()
    else:
        print_help()
        exit(1)


if __name__ == "__main__":
    main()


# parser = ArgumentParser()
#
# parser_command = parser.add_subparsers(title='commands',dest='command',required=True)
#
# parser_command_configure = parser_command.add_parser('configure', help="Configure profile")
# parser_command_configure.add_argument('-p', '--profile', dest='profile', help='Profile name')
# parser_command_configure.add_argument('--replace', action='store_true', dest='replace', help='Replace profile config and credentials')
# parser_command_configure.add_argument('--replace-config', action='store_true', dest='preserve_config', help='Replace profile config')
# parser_command_configure.add_argument('--replace-credentials', action='store_true', dest='preserve_credentials', help='Replace profile credentials')
#
# parser_command_configure.add_argument(dest='options', nargs='+', help='Profile options')
# parser_command_configure.set_defaults(func=profile_configure)
#
# parser_command_delete = parser_command.add_parser('delete', help='Delete profile')
# parser_command_delete.add_argument('-p', '--profile', dest='profile', help='Profile name')
# parser_command_delete.add_argument('--preserve-config', action='store_true', dest='delete_config', help='Preserve profile config')
# parser_command_delete.add_argument('--preserve-credentials', action='store_true', dest='delete_credentials', help='Preserve profile credentials')
# parser_command_delete.set_defaults(func=profile_delete)
#
# args = parser.parse_args()
# args.func(args)
