import argparse
import os
import re

from github3api import GitHubAPI
from semantic_version import Version
from colors import *

from images import get_image_versions

def get_client():
    try:
        gh_token = os.getenv('GH_TOKEN_PSW')

        try:
            cabundle = os.getenv('REQUESTS_CA_BUNDLE')
        except KeyError:
            cabundle = None

        if cabundle:
            client = GitHubAPI(bearer_token=gh_token, cabundle=cabundle)
        else:
            client = GitHubAPI(bearer_token=gh_token)

        return client
    except KeyError:
        print("Please provide [GH_TOKEN_PSW] env var")
        raise KeyError

def main():
    args = parse_args()
    client = get_client()

    print("Rate Limit --->", client.get('/rate_limit')['resources']['core'])

    # allow just to lookup a single repo
    repo = args.repo
    if args.repo is not None:
        version = get_latest(client, repo, args.org)
        print(f"{args.org}/{repo} latest released version v{version}")
    else:
        envfile = read_env_file(args.envfile)
        compose_env_vars = env_to_dict(envfile)

        if args.no_lookup is False:
            print(f"Determining latest versions. Please wait...")

            # update REPOSITORY keys
            for key in compose_env_vars:
                if 'REPOSITORY' in key:
                    compose_env_vars[key] = 'edgexfoundry'

            repo_map = {
                'edgex-go': 'CORE_EDGEX_VERSION',
                'app-service-configurable': 'APP_SERVICE_VERSION',
                'edgex-ui-go': 'EDGEX_UI_VERSION',
                'device-bacnet-c': 'DEVICE_BACNET_VERSION',
                'device-camera-go': 'DEVICE_CAMERA_VERSION',
                'device-grove-c': 'DEVICE_MQTT_VERSION',
                'device-modbus-go': 'DEVICE_MODBUS_VERSION',
                'device-mqtt-go': 'DEVICE_MQTT_VERSION',
                'device-random': 'DEVICE_RANDOM_VERSION',
                'device-rest-go': 'DEVICE_REST_VERSION',
                'device-snmp-go': 'DEVICE_SNMP_VERSION',
                'device-virtual-go': 'DEVICE_VIRTUAL_VERSION',
            }

            total = len(repo_map)
            counter = 1
            for repo in repo_map:
                print(f"[{counter}/{total}] Fetching tags for {args.org}/{repo}")
                version = get_latest(client, repo, args.org)
                version_key = repo_map[repo]
                compose_env_vars[version_key] = f"{version}"
                counter += 1

            print(f"Done with versions...Writing env file")

        write_env_file(envfile, compose_env_vars, args.out)

        print("-----------------------------------------------------------------------")
        print(f"Complete...Generated env file to [{args.out}]")
        print()

        updated_versions = {}
        if args.no_deps is False:
            print("----")
            print()
            print(f"Looking up dependency version for [{args.deps}]")
            updated_versions = lookup_dependencies(compose_env_vars, args.deps)

        if len(updated_versions) > 0:
            print("")
            print(color("=============================================================================", fg='red'))
            print(color("!!! Updated dependency versions have been found in case you want to updated", fg='red'))
            print(color("=============================================================================", fg='red'))
            for key in updated_versions:
                print(color(f"{key}={updated_versions[key]}", fg='yellow'))

def env_to_dict(envfile):
    compose_env_vars = {}
    for line in envfile:
        line = line.strip()
        if '=' in line:
            (key, val) = line.split('=', 1)
            compose_env_vars[key] = val
    return compose_env_vars

def read_env_file(file=None):
    if file is None:
        file = './.env'

    envfile = []
    with open(file) as f:
        for line in f:
            envfile.append(line)
    return envfile

def write_env_file(envfile, compose_env_vars, outfile):
    with open(outfile, 'w') as env_file:
        # rewrite the file with comments
        for line in envfile:
            if '=' in line:
                (key, val) = line.split('=', 1)
                print(f"{key}={compose_env_vars[key]}")
                env_file.write(f"{key}={compose_env_vars[key]}\n")
            else:
                print(line, end='')
                env_file.write(line)

def lookup_dependencies(current_versions, deps):
    updated_versions = {}

    for dep in deps.split(' '):
        env_file_version_key = f"{dep.upper()}_VERSION"
        current_version = current_versions[env_file_version_key]
        if current_version:
            is_alpine = 'alpine' in current_version

            lookup = 'alpine' if is_alpine else 'latest'
            org = 'library'
            rollup = True

            if dep == 'kuiper':
                org = 'emqx'
                rollup = False

            if dep == 'mosquitto':
                image_name = 'eclipse-mosquitto'
            else:
                image_name = dep

            dep_version = get_image_versions(image_name, org=org, filter=lookup, rollup=rollup, verbose=False)

            all_versions = dep_version[lookup]
            # deal with alpine versions a bit different

            version = None  # this should always be the patch semver version
            if is_alpine:
                regex = '^([0-9]|[1-9][0-9]*)\.([0-9]|[1-9][0-9]*)\.([0-9]|[1-9][0-9]*)-alpine$'

                for v in all_versions:
                    if re.search(regex, v):
                        version = v
                        break
            else:
                version = all_versions[0]

            if version is not None:
                if current_version != version:
                    updated_versions[env_file_version_key] = f"{current_version} --> {version}"
            else:
                print(f"Unable to find version for {dep}")

    return updated_versions

def get_latest(client, repo, org='edgexfoundry'):
        tags = client.get(f'/repos/{org}/{repo}/tags', _get='all')

        released_versions = []
        for tag in tags:
            name = tag['name']
            if name.startswith('v'):
                semver_version = Version(name[1:])
            else:
                semver_version = Version(name)

            if not semver_version.prerelease:
                released_versions.append(semver_version)

        return released_versions[0]

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='docker image tag lookup')

    parser.add_argument('--repo', required=False, default=None,
                        help=('The repo to lookup tags'))

    parser.add_argument('--org', required=False, default='edgexfoundry',
                        help=('The organization to lookup'))

    parser.add_argument('--envfile', required=False, default='./.env',
                        help=('compose env file to read'))

    parser.add_argument('--out', required=False, default='./.env.new',
                        help=('where to write the generated env file'))

    parser.add_argument('--no-lookup', action='store_true',
                        help='do not lookup edgex versions')

    # these two go together
    parser.add_argument('--no-deps', action='store_true',
                        help='do not lookup dependency versions')
    parser.add_argument('--deps', required=False, default='vault consul redis kong kuiper mosquitto',
                        help=('dependency versions to lookup'))

    return parser.parse_args()

if __name__ == "__main__":
    main()
