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

    if not merge:
        profile_delete(config_path, profile_section, clear=True)

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
        output = True
        for config_line in StringIO(config_string):
            section_match = ConfigFileWriter.SECTION_REGEX.search(config_line)
            if section_match:
                if section_match.group('header') == profile_section:
                    if clear:
                        config_file.write(config_line)
                    output = False
                else:
                    if clear and not output:
                        config_file.write('\n')
                    output = True
            if output:
                config_file.write(config_line)


def print_help():
    print("""\
usage:

    list profiles:

        aws-configure list
        

    set profile options:

        aws-configure set [--profile/-p <profile_name>] [--clean/-c] [<config_options...>]

            --profile/-p <profile_name> : select profile ['default']
            <config_options>            : key=value pairs e.g. 'region=eu-central-1' 'source_profile=default'
            --empty/-e                  : empty all profile options before setting new options
            --empty-config              : empty profile config options before setting
            --empty-credentials         : empty profile credentials options before setting

    get profile options:

        aws-configure get [--profile/-p <profile_name>] [<config_options...>]

            --profile/-p <profile_name> : select profile ['default']
            <config_options>            : option key e.g. 'region' 'source_profile'

    delete profile:

        aws-configure delete [--profile/-p <profile_name>] [--config] [--credentials]

            --profile/-p <profile_name> : select profile ['default']
            --config                    : delete only profile config in '~/.aws/config'
            --credentials               : delete only profile credentials in '~/.aws/credentials'

    print help

        aws-configure help
""")

def handle_help(args):
    print_help()

def handle_list_profiles(args):
    profile_map = Session().full_config['profiles']
    for profile_name, profile in profile_map.items():
        print(profile_name)


def handle_delete_profile(args):
    profile_name = args.profile_name or 'default'
    delete_all= not args.delete_config and not args.delete_credentials
    delete_config = delete_all or args.delete_config
    delete_credentials = delete_all or args.delete_credentials

    if delete_config:
        print("delete profile config")
        profile_delete(aws_config_path, profile_config_section(profile_name))

    if delete_credentials:
        print("delete profile credentials")
        profile_delete(aws_credentials_path, profile_name)


def handle_set_profile(args):
    profile_name = args.profile_name or 'default'
    profile_config = {}
    profile_credentials = {}
    for option in args.profile_options:
        option = split_key_value(option, '=')
        if option.key not in ['aws_access_key_id', 'aws_secret_access_key', 'aws_session_token']:
            profile_config[option.key] = option.value
        else:
            profile_credentials[option.key] = option.value

    if args.empty_config or args.empty_all:
        print("empty profile config")
        profile_update(aws_config_path, profile_config_section(profile_name),{})

    if profile_config:
        print("set profile config")
        profile_update(aws_config_path, profile_config_section(profile_name),
                       profile_config, merge=True)

    if args.empty_credentials or args.empty_all:
        print("empty profile credentials")
        profile_update(aws_credentials_path, profile_name,{})

    if profile_credentials:
        print("set profile credentials")
        profile_update(aws_credentials_path, profile_name,
                       profile_credentials, merge=True)


def handle_get_profile(args):
    profile_name = args.profile_name or 'default'
    aws_config_section=profile_config_section(profile_name)
    aws_config = ConfigParser()
    aws_config.read(aws_config_path)
    if args.profile_options:
        for option in args.profile_options:
            print(aws_config.get(aws_config_section, option))
    else:
        for option in aws_config.options(aws_config_section):
            print(f'{option} = {aws_config.get(aws_config_section, option)}')
            
            
def main():
    parser = ArgumentParser(add_help=False)

    parser_command = parser.add_subparsers(title='commands',dest='command',required=True)

    parser_command_list = parser_command.add_parser('list', help="List profiles")
    parser_command_list.set_defaults(func=handle_list_profiles)

    parser_command_set = parser_command.add_parser('set', help="Set profile options")
    parser_command_set.add_argument('-p', '--profile', dest='profile_name', help='Profile name')
    parser_command_set.add_argument('-e', '--empty', action='store_true', dest='empty_all', help='Empty all profile options before setting new options')
    parser_command_set.add_argument('--empty-config', action='store_true', dest='empty_config', help='Empty profile config options before setting new options')
    parser_command_set.add_argument('--empty-credentials', action='store_true', dest='empty_credentials', help='Empty profile credentials options before setting new options')
    parser_command_set.add_argument(dest='profile_options', nargs='*', help='Profile options')
    parser_command_set.set_defaults(func=handle_set_profile)
    
    parser_command_get = parser_command.add_parser('get', help="Get profile options")
    parser_command_get.add_argument('-p', '--profile', dest='profile_name', help='Profile name')
    parser_command_get.add_argument(dest='profile_options', nargs='*', help='Profile options')
    parser_command_get.set_defaults(func=handle_get_profile)

    parser_command_delete = parser_command.add_parser('delete', help='Delete profile')
    parser_command_delete.add_argument('-p', '--profile', dest='profile_name', help='Profile name')
    parser_command_delete.add_argument('--config', action='store_true', dest='delete_config', help='Delete only profile config')
    parser_command_delete.add_argument('--credentials', action='store_true', dest='delete_credentials', help='Delete only profile credentials')
    parser_command_delete.set_defaults(func=handle_delete_profile)
    
    parser_command_help = parser_command.add_parser('help', help="Print help")
    parser_command_help.set_defaults(func=handle_help)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
