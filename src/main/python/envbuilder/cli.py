# Copyright (c) 2020 Intel Corporation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging
import os
import re

from colors import color

from envbuilder import API
from envbuilder import DockerImageSearch

logger = logging.getLogger(__name__)

class EnvBuilder():
    def __init__(self, args):
        self.args = args
        self.image_search = DockerImageSearch()
        self.api = self.get_client()

        self.envfile = EnvBuilder.read_env_file(args.envfile)
        self.compose_env_vars = EnvBuilder.env_to_dict(self.envfile)
        self.docker_repository = 'edgexfoundry'

        self.repo_map = {
            'edgex-go': 'CORE_EDGEX_VERSION',
            'app-service-configurable': 'APP_SERVICE_VERSION',
            'edgex-ui-go': 'EDGEX_UI_VERSION',
            'device-bacnet-c': 'DEVICE_BACNET_VERSION',
            'device-camera-go': 'DEVICE_CAMERA_VERSION',
            'device-grove-c': 'DEVICE_GROVE_VERSION',
            'device-modbus-go': 'DEVICE_MODBUS_VERSION',
            'device-mqtt-go': 'DEVICE_MQTT_VERSION',
            'device-random': 'DEVICE_RANDOM_VERSION',
            'device-rest-go': 'DEVICE_REST_VERSION',
            'device-snmp-go': 'DEVICE_SNMP_VERSION',
            'device-virtual-go': 'DEVICE_VIRTUAL_VERSION',
        }

    def process_env_file(self):
        if self.args.no_lookup is False:
            logger.info("Determining latest versions. Please wait...")

            # update REPOSITORY keys
            for key in self.compose_env_vars:
                if 'REPOSITORY' in key:
                    self.compose_env_vars[key] = self.docker_repository

            self.process_tags()

            logger.info("Done with versions...Writing env file")

        # not sure this should be static
        EnvBuilder.write_env_file(
            self.envfile, self.compose_env_vars, self.args.out)

        logger.info(
            "-----------------------------------------------------------------------")
        logger.info(f"Complete...Generated env file to [{self.args.out}]")
        logger.info("")

        updated_versions = {}
        if self.args.no_deps is False:
            logger.info("----")
            logger.info("")
            logger.info(
                f"Looking up dependency version for [{self.args.deps}]")
            updated_versions = self.lookup_dependencies(self.args.deps)

        if len(updated_versions) > 0:
            logger.info("")
            logger.info(color(
                "=============================================================================", fg='red'))
            logger.info(color(
                "!!! Updated dependency versions have been found in case you want to updated", fg='red'))
            logger.info(color(
                "=============================================================================", fg='red'))
            for key in updated_versions:
                logger.info(
                    color(f"{key}={updated_versions[key]}", fg='yellow'))

    def process_tags(self):
        total = len(self.repo_map)
        counter = 1
        for repo in self.repo_map:
            logger.info(
                f"[{counter}/{total}] Fetching tags for {self.args.org}/{repo}")

            version = self.api.get_latest(repo, self.args.org)
            version_key = self.repo_map[repo]
            self.compose_env_vars[version_key] = f"{version}"
            counter += 1

    def get_client(self):
        '''Get GitHub API instance'''
        try:
            gh_token = os.getenv('GH_TOKEN_PSW')

            try:
                cabundle = os.getenv('REQUESTS_CA_BUNDLE')
            except KeyError:
                cabundle = None

            if cabundle:
                client = API(bearer_token=gh_token, cabundle=cabundle)
            else:
                client = API(bearer_token=gh_token)

            return client
        except KeyError:
            print("Please provide [GH_TOKEN_PSW] env var")
            raise KeyError

    def rate_limit(self):
        results = self.api.get('/rate_limit')['resources']['core']
        return results

    def lookup_dependencies(self, deps):
        updated_versions = {}

        for dep in deps.split(' '):
            env_file_version_key = f"{dep.upper()}_VERSION"
            current_version = self.compose_env_vars[env_file_version_key]

            if current_version:
                is_alpine = 'alpine' in current_version

                lookup = 'alpine' if is_alpine else 'latest'
                org = 'library'

                # all this if/else is pretty ugly
                if dep == 'kuiper':
                    org = 'emqx'

                if dep == 'mosquitto':
                    image_name = 'eclipse-mosquitto'
                else:
                    image_name = dep

                dep_version = self.image_search.get_image_versions(
                    image_name, org=org, filter=lookup, verbose=False)

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

    @staticmethod
    def read_env_file(path='./.env'):
        envfile = []
        with open(path) as f:
            for line in f:
                envfile.append(line)
        return envfile

    @staticmethod
    def env_to_dict(envfile):
        compose_env_vars = {}
        for line in envfile:
            line = line.strip()
            if '=' in line:
                (key, val) = line.split('=', 1)
                compose_env_vars[key] = val
        return compose_env_vars

    @staticmethod
    def write_env_file(envfile, custom_versions, outfile):
        '''Merge and write env file'''
        with open(outfile, 'w') as env_file:
            # rewrite the file with comments
            for line in envfile:
                if '=' in line:
                    (key, val) = line.split('=', 1)
                    s = f"{key}={custom_versions[key]}"
                    print(s)
                    env_file.write(f"{s}\n")
                else:
                    print(line, end='')
                    env_file.write(line)


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

    parser.add_argument('--verbose', action='store_true',
                        help='verbose logging')

    # these two go together
    parser.add_argument('--no-deps', action='store_true',
                        help='do not lookup dependency versions')
    parser.add_argument('--deps', required=False, default='vault consul redis kong kuiper mosquitto',
                        help=('dependency versions to lookup'))

    return parser.parse_args()


def set_logging(args):
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    formatter = '%(asctime)s [%(funcName)s] %(levelname)s %(message)s'
    stream_formatter = logging.Formatter(formatter)
    stream_handler.setFormatter(stream_formatter)
    stream_handler.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    rootLogger.addHandler(stream_handler)


def main():
    args = parse_args()
    set_logging(args)

    builder = EnvBuilder(args)

    logger.info(f"Rate Limit ---> {builder.rate_limit()}")

    # allow just to lookup a single repo
    repo = args.repo
    if args.repo is not None:
        version = builder.api.get_latest(repo, args.org)
        logger.info(f"{args.org}/{repo} latest released version v{version}")
    else:
        builder.process_env_file()


if __name__ == "__main__":
    main()
