
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

import re
import logging
from datetime import datetime
from datetime import timedelta

from requests.exceptions import HTTPError
from requests.exceptions import SSLError
from requests.exceptions import ProxyError
from requests.exceptions import ConnectionError
from pytz import timezone
from github3api import GitHubAPI

logger = logging.getLogger(__name__)


class API(GitHubAPI):

    def __init__(self, **kwargs):
        logger.debug('executing API constructor')

        if not kwargs.get('bearer_token'):
            raise ValueError('bearer_token must be provided')

        super(API, self).__init__(**kwargs)

    def get_repos(self, organization=None, user=None, regex='', exclude_repos=None, **attributes):
        """ return organization repos that match the provided attributes
        """
        if not exclude_repos:
            exclude_repos = []
        endpoint = f'/orgs/{organization}/repos'
        if user:
            endpoint = f'/users/{user}/repos'
        repos = self.get(endpoint, _get='all')
        if not regex and not attributes:
            return repos
        matched_repos = API.match_key_values(repos, regex=regex, **attributes)
        return [
            repo['name']
            for repo in matched_repos
            if repo['name'] not in exclude_repos
        ]

    def get_labels(self, repo):
        """ return labels contained in repo
            repo must be formatted as ':owner/:repo'
            GET /repos/:owner/:repo/labels
        """
        return self.get(
            f'/repos/{repo}/labels',
            _get='all',
            _attributes=[
                'name',
                'description',
                'color'
            ])

    def get_milestones(self, repo):
        """ return milestones contained in repo
            repo must be formatted as ':owner/:repo'
            GET /repos/:owner/:repo/milestones
        """
        return self.get(
            f'/repos/{repo}/milestones',
            _get='all',
            _attributes=[
                'number',
                'title',
                'state',
                'description',
                'due_on'
            ])

    def exists(self, endpoint):
        """ return True if resource associated with endpoint exists, False otherwise
        """
        try:
            logger.debug(f'checking if resource associated with {endpoint} exists')
            self.get(endpoint, raw_response=True)
            return True
        except HTTPError as exception:
            if exception.response.status_code == 404:
                return False
            raise exception

    def modify(self, endpoint, payload, resource_id=None, noop=False):
        """ modify resource using PATCH endpoint
        """
        self.patch(endpoint, json=payload, noop=noop)
        resource_id = resource_id if resource_id else API.get_resource_id(endpoint)
        logger.info(f"modified {API.get_resource(endpoint)} '{resource_id}' in repo '{API.get_owner_repo(endpoint)}' - NOOP: {noop}")

    def create(self, endpoint, payload, resource_id, noop=False):
        """ create resource using POST endpoint
        """
        self.post(endpoint, json=payload, noop=noop)
        logger.info(f"created {API.get_resource(endpoint, index=-1)} '{payload.get(resource_id)}' in repo '{API.get_owner_repo(endpoint)}' - NOOP: {noop}")

    def sync_labels(self, repo, labels, source_repo, modified_since=None, noop=True):
        """ sync labels to repo
            repo must be formatted as ':owner/:repo'
        """
        logger.info(f"synchronizing {len(labels)} labels to repo '{repo}'")
        endpoint = f'/repos/{repo}/labels'
        for label in labels:
            name = label['name']
            label_endpoint = f'{endpoint}/{name}'
            source_endpoint = f'/repos/{source_repo}/labels/{name}'
            if self.exists(label_endpoint):
                if self.modified_since(source_endpoint, modified_since):
                    self.modify(label_endpoint, label, noop=noop)
                else:
                    logger.info(f"label '{name}' in repo '{repo}' has not been modified since '{modified_since}'")
            else:
                self.create(endpoint, label, 'name', noop=noop)
        logger.info(f"synchronization of labels to repo '{repo}' is complete")

    def sync_milestones(self, repo, milestones, source_repo, modified_since=None, noop=True):
        """ sync milestones to repo
            repo must be formatted as ':owner/:repo'
        """
        logger.info(f"synchronizing {len(milestones)} milestones to repo '{repo}'")
        repo_milestones = self.get_milestones(repo)
        endpoint = f'/repos/{repo}/milestones'
        for milestone in milestones:
            repo_milestone = API.search(repo_milestones, 'title', milestone['title'])
            if repo_milestone:
                milestone_number = milestone.pop('number')
                source_endpoint = f'/repos/{source_repo}/milestones/{milestone_number}'
                if self.modified_since(source_endpoint, modified_since):
                    repo_milestone_number = repo_milestone['number']
                    target_endpoint = f'{endpoint}/{repo_milestone_number}'
                    self.modify(target_endpoint, milestone, resource_id=milestone['title'], noop=noop)
                else:
                    logger.info(f"milestone '{milestone['title']}' in repo '{repo}' has not been modified since '{modified_since}'")
            else:
                milestone.pop('number')
                sanitized_milestone = {key: value for key, value in milestone.items() if value is not None}
                self.create(endpoint, sanitized_milestone, 'title', noop=noop)
        logger.info(f"synchronization of milestones to repo '{repo}' is complete")

    def sync_repos(self, source_repo, organization=None, user=None, regex='', exclude_repos=None, modified_since=None, noop=False):
        """ sync labels and milestones in source_repo to all matching repos in organization or user
        """
        owner = organization if organization else user
        repos = self.get_repos(organization=organization, user=user, regex=regex, exclude_repos=exclude_repos, archived=False, disasbled=False)
        logger.info(f"retrieved {len(repos)} repos in '{owner}'")

        labels = self.get_labels(source_repo)
        logger.info(f"retrieved {len(labels)} labels from repo '{source_repo}'")

        milestones = self.get_milestones(source_repo)
        logger.info(f'retrieved {len(milestones)} milestones from repo {source_repo}')

        for repo in repos:
            repo_name = f'{owner}/{repo}'
            self.sync_labels(repo_name, labels, source_repo, noop=noop)
            self.sync_milestones(repo_name, milestones, source_repo, noop=noop)

    def modified_since(self, endpoint, modified_since):
        """ return True if endpoint has been modified since modified_since
        """
        if not modified_since:
            return True
        logger.debug(f'checking if resource associated with {endpoint} has been modified since {modified_since}')
        response = self.get(
            endpoint,
            raw_response=True,
            headers={
                'If-Modified-Since': modified_since
            })
        modified = response.status_code == 200
        logger.debug(f"resource associated with {endpoint} {'has been' if modified else 'has not been'} modified since {modified_since}")
        return modified

    @staticmethod
    def log_ratelimit(ratelimit):
        """ log rate limit data - override of base class
        """
        logger.info(f"{ratelimit['remaining']}/{ratelimit['limit']} resets in {ratelimit['minutes']} min")

    @staticmethod
    def match_key_values(items, regex='', **attributes):
        """ return list of items whose name matches regex and key values match attributes
        """
        matched_items = []
        for item in items:
            if re.match(regex, item['name']) and all(item[key] == value for key, value in attributes.items() if key in item):
                matched_items.append(item)
        return matched_items

    @staticmethod
    def get_resource_id(endpoint):
        """ return resource id from endpoint
        """
        return endpoint.split('/')[-1]

    @staticmethod
    def get_resource(endpoint, index=-2):
        """ return resource from endpoint
        """
        return endpoint.split('/')[index][:-1]

    @staticmethod
    def get_owner_repo(endpoint):
        """ return owner repo from endpoint
        """
        return '/'.join(endpoint.split('/')[2:4])

    @staticmethod
    def get_gmt_time(delta):
        """ return gmtime formatted with delta applied
        """
        if not delta:
            return
        match = re.match('^(?P<value>\d+)(?P<unit>[dmh])$', delta)
        if not match:
            raise ValueError('last modified not formatted properly')

        value = int(match.group('value'))
        unit = match.group('unit')
        gmt_time = datetime.now(timezone('GMT'))
        if unit == 'd':
            delta_time = gmt_time - timedelta(days=value)
        elif unit == 'm':
            delta_time = gmt_time - timedelta(minutes=value)
        elif unit == 'h':
            delta_time = gmt_time - timedelta(hours=value)

        return delta_time.strftime("%a, %d %b %Y %H:%M:%S %Z")

    @staticmethod
    def search(items, key, value):
        """ return item in items whose key equals value
        """
        for item in items:
            if item[key] == value:
                return item

    @staticmethod
    def retry_connection_error(exception):
        """ return True if exception is SSLError, ProxyError or ConnectError, False otherwise
            retry:
                wait_random_min:10000
                wait_random_max:20000
                stop_max_attempt_number:6
        """
        logger.debug(f"checking if '{type(exception).__name__}' exception is a connection error")
        if isinstance(exception, (SSLError, ProxyError, ConnectionError)):
            logger.info('connectivity error encountered - retrying request shortly')
            return True
        logger.debug(f'exception is not a connectivity error: {exception}')
        return False
