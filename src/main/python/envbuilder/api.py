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

        return released_versions[0]
