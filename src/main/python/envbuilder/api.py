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

import logging

from github3api import GitHubAPI
from semantic_version import Version

from requests.exceptions import SSLError
from requests.exceptions import ProxyError
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)


class API(GitHubAPI):
    def __init__(self, **kwargs):
        logger.debug('executing API constructor')

        if not kwargs.get('bearer_token'):
            raise ValueError('bearer_token must be provided')

        super(API, self).__init__(**kwargs)

    def get_latest(self, repo, org='edgexfoundry'):
        tags = self.get(f'/repos/{org}/{repo}/tags', _get='all')

        released_versions = []
        for tag in tags:
            name = tag['name']
            if name.startswith('v'):
                semver_version = Version(name[1:])
            else:
                semver_version = Version(name)

            if not semver_version.prerelease:
                released_versions.append(semver_version)

        return released_versions[0] if len(released_versions) > 0 else None

    @staticmethod
    def retry_connection_error(exception):
        """ return True if exception is SSLError, ProxyError or ConnectError, False otherwise
            retry:
                wait_random_min:10000
                wait_random_max:20000
                stop_max_attempt_number:6
        """
        logger.debug(
            f"checking if '{type(exception).__name__}' exception is a connection error")
        if isinstance(exception, (SSLError, ProxyError, ConnectionError)):
            logger.info(
                'connectivity error encountered - retrying request shortly')
            return True
        logger.debug(f'exception is not a connectivity error: {exception}')
        return False
