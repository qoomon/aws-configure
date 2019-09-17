# aws-configure

[![PyPI](https://img.shields.io/pypi/v/aws-configure?)](https://pypi.org/project/aws-configure/)

A CLI to configure AWS named profiles in `~/.aws/config` and `~/.aws/credentials files

## Usage
``` 
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
``` 

## Setup dev environment

#### Install Dev Dependencies
`pip3 install -r requirements.txt`
`pip3 install -r requirements-dev.txt`

#### Create Package
`python3 setup.py sdist bdist_wheel`

#### Local Install
`pip3 install --force-reinstall --no-deps dist/aws_configure-*-py3-none-any.whl`

#### Deploy to PiPy
`twine upload dist/*`
