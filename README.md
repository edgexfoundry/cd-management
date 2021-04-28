# edgex-compose-builder

[![GitHub Pull Requests](https://img.shields.io/github/issues-pr-raw/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/pulls) [![GitHub Contributors](https://img.shields.io/github/contributors/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/contributors) [![GitHub Committers](https://img.shields.io/badge/team-committers-green)](https://github.com/orgs/edgexfoundry/teams/devops-core-team/members) [![GitHub Commit Activity](https://img.shields.io/github/commit-activity/m/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/commits)

## Summary

This python script will update the `edgex-compose/compose-builder/.env` file with the `latest` versions for a given release.

## Pipeline Summary

### Parameters

* **BRANCH** (string) Named branch to create (typically this will be the release name)
* **PUSH_BRANCH** (boolean) Where or not to push the branch to GitHub

The Jenkins automation combines the python script with the compose builder `make` scripts. The automation will generate the env file then will stash the file. The next stage will unstash the env file in the proper directory and will

## Local Usage

Local script usage requires a GitHub [Personal Access Token](https://github.com/settings/tokens) exported to the environment as `GH_TOKEN_PSW`

```bash
$ pip install -r requirements.txt
$ export GH_TOKEN_PSW=<secret>

                         __          _ __    __
  ___  ____ _   __      / /_  __  __(_) /___/ /__  _____
 / _ \/ __ \ | / /_____/ __ \/ / / / / / __  / _ \/ ___/
/  __/ / / / |/ /_____/ /_/ / /_/ / / / /_/ /  __/ /
\___/_/ /_/|___/     /_.___/\__,_/_/_/\__,_/\___/_/


usage: env-builder.py [-h] [--repo REPO] [--org ORG] [--envfile ENVFILE] [--out OUT] [--no-lookup] [--no-deps] [--deps DEPS]

docker image tag lookup

optional arguments:
  -h, --help         show this help message and exit
  --repo REPO        The repo to lookup tags (default: None)
  --org ORG          The organization to lookup (default: edgexfoundry)
  --envfile ENVFILE  compose env file to read (default: ./.env)
  --out OUT          where to write the generated env file (default: ./.env.new)
  --no-lookup        do not lookup edgex versions (default: False)
  --no-deps          do not lookup dependency versions (default: False)
  --deps DEPS        dependency versions to lookup (default: vault consul redis kong kuiper mosquitto)
```

## Reference

[![asciicast](https://asciinema.org/a/a118Tao1I65u8EtM4yRxWKYOy.svg)](https://asciinema.org/a/a118Tao1I65u8EtM4yRxWKYOy)

## Examples

If you just want to check the latest version of a specific repository you can run this command:

```bash
$ python env-builder.py --org edgexfoundry --repo edgex-go
edgexfoundry/edgex-go latest released version v1.3.1

$ python env-builder.py --org edgexfoundry --repo device-random
edgexfoundry/device-random latest released version v1.3.1
```

The script will look for a `.env` file in the root of this directory, however you can override that location. You can also override the output location of the generated `.env` file.

```bash
$ python env-builder.py --envfile edgex-compose/compose-builder/.env --out ./.my-env-file
... truncated output
...
Complete...Generated env file to [./.my-env-file]
...
```

The script will attempt to download the latest version of installed dependencies. You can turn this behavior off by passing the `--no-deps`

```bash
$ python env-builder.py --envfile edgex-compose/compose-builder/.env --no-deps
... truncated output
```

If you want to disable latest version lookup in the script, you can pass the `--no-lookup` option. This will essentially just create a copy of the existing env file. You can think of this a the NOOP mode. Good for quickly checking for new dependency versions.

```bash
$ python env-builder.py --envfile edgex-compose/compose-builder/.env --no-lookup
... truncated output
```

## With Docker

```bash
docker build -t edgex-compose-builder:latest -f Dockerfile.build .

docker run --rm \
  -v $PWD:/code -w /code \
  -e GH_TOKEN_PSW \
  edgex-compose-builder:latest \
  python env-builder.py --envfile ./edgex-compose/compose-builder/.env
```
