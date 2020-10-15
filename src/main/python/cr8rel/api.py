
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

import os
import logging

from magic import Magic
from requests.exceptions import SSLError
from requests.exceptions import ProxyError
from requests.exceptions import ConnectionError
from uritemplate import URITemplate
from uritemplate import expand
from github3api import GitHubAPI

logger = logging.getLogger(__name__)


class ReleaseAlreadyExists(Exception):
    pass


class API(GitHubAPI):

    def __init__(self, **kwargs):
        logger.debug('executing API constructor')

        if not kwargs.get('bearer_token'):
            raise ValueError('bearer_token must be provided')

        retries = [{
            'retry_on_exception': API.is_connection_error,
            'wait_random_min': 10000,
            'wait_random_max': 20000,
            'stop_max_attempt_number': 6
        }]

        super(API, self).__init__(retries=retries, **kwargs)

        self.items_to_redact.append('data')

    def create_release_upload_assets(self, repo, tag_name, directory, release_name=None, description=None):
        """ create release on repo and upload assets from directory
        """
        release = self.create_release(repo, tag_name, release_name=release_name, description=description)
        self.upload_assets(directory, release)

    def validate_release(self, repo, tag_name, release_name):
        """ validate release with specified meta-data does not exist
        """
        releases = self.get(f'/repos/{repo}/releases', _get='all', _attributes=['id', 'name', 'tag_name'])
        for release in releases:
            if tag_name == release['tag_name']:
                raise ReleaseAlreadyExists(f"A release with tag {release['tag_name']} already exists")
            if release_name == release['name']:
                raise ReleaseAlreadyExists(f"A release with name {release['name']} already exists")

    def create_release(self, repo, tag_name, release_name=None, description=None):
        """ create release for repo with specified meta-data
        """
        if not release_name:
            release_name = tag_name
        if not description:
            description = tag_name

        self.validate_release(repo, tag_name, release_name)

        logger.info(f'creating release {release_name} with tag {tag_name} description {description} on repo {repo}')
        response = self.post(
            f'/repos/{repo}/releases',
            json={
                'tag_name': tag_name,
                'name': release_name,
                'body': description
            })

        response['repo'] = repo
        return response

    def upload_assets(self, directory, release):
        """ upload all assets in directory to release
        """
        assets = API.get_assets(directory)
        for asset in assets:
            self.upload_asset(asset, release)

    def upload_asset(self, asset, release):
        """ upload asset to release
        """
        logger.info(f"uploading asset {asset['name']} to repo {release['repo']} release {release['name']}")
        self.post(
            API.get_upload_url(release['upload_url'], asset['name'], asset['label']),
            headers={'Content-Type': asset['content-type']},
            data=asset['content'])

    @staticmethod
    def get_assets(directory):
        """ return assets discovered in directory
        """
        assets = []
        for _, _, files in os.walk(directory):
            for file in files:
                assets.append({
                    'name': file,
                    'label': None,
                    'content': API.get_content(os.path.join(directory, file)),
                    'content-type': API.get_content_type(file)
                })
        return assets

    @staticmethod
    def get_upload_url(upload_url_template, name, label):
        """ return upload url from upload uri template
        """
        uri_template = URITemplate(upload_url_template)
        return uri_template.expand(name=name, label=label)

    @staticmethod
    def get_content(file_name):
        """ read and return content of file
        """
        with open(file_name, 'rb') as in_file:
            content = in_file.read()
        return content

    @staticmethod
    def get_content_type(file_name):
        """ return associated content type for file
        """
        try:
            return Magic(mime=True).from_file(file_name)
        except:
            return 'text/plain'

    @staticmethod
    def is_connection_error(exception):
        """ return True if exception is SSLError, ProxyError or ConnectError, False otherwise
        """
        logger.debug(f'checking exception for retry candidacy: {type(exception).__name__}')
        if isinstance(exception, (SSLError, ProxyError, ConnectionError)):
            logger.info('connectivity error - retrying request in a few seconds')
            return True
        return False
