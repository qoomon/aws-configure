# aws-configure

[![PyPI](https://img.shields.io/pypi/v/aws-configure?)](https://pypi.org/project/aws-configure/)

A CLI to configure AWS named profiles in `~/.aws/config` and `~/.aws/credentials files`

## Usage
```
list profiles:

      aws-configure list
      

  set profile options:

      aws-configure set [--profile/-p <profile_name>] [<config_options...>]

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
```

### Bash Helper Scripts
#### Export Credentials To Current Bash Session
```
function aws-export-credentials {
  local profile="$1"
  { 
    read AWS_ACCESS_KEY_ID 
    read AWS_SECRET_ACCESS_KEY 
    read AWS_SESSION_TOKEN
  } <<< $(
    aws-configure get -p "$profile" \
      aws_access_key_id \
      aws_secret_access_key \
      aws_session_token
    )
  export AWS_ACCESS_KEY_ID 
  export AWS_SECRET_ACCESS_KEY 
  export AWS_SESSION_TOKEN
}
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
