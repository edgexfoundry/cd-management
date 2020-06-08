
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
from os import getenv
from rest3client import RESTclient
from requests.exceptions import HTTPError
from requests.exceptions import SSLError
from requests.exceptions import ProxyError
from ratelimit import limits
from ratelimit import sleep_and_retry
from retrying import retry
from pytz import timezone
from datetime import datetime
from datetime import timedelta

import logging
logger = logging.getLogger(__name__)

logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)

HOSTNAME = 'api.github.com'


def match_key_values(items, regex='', **attributes):
    """ return list of items whose name matches regex and key values match attributes
    """
    matched_items = []
    for item in items:
        if re.match(regex, item['name']) and all(item[key] == value for key, value in attributes.items() if key in item):
            matched_items.append(item)
    return matched_items


def match_keys(items, attributes):
    """ return list of items with matching keys from list of attributes
    """
    if not attributes:
        return items
    matched_items = []
    for item in items:
        matched_items.append({
            key: item[key] for key in attributes if key in item
        })
    return matched_items


def log_ratelimit(headers):
    """ convert and log rate limit data
    """
    reset = headers.get('X-RateLimit-Reset')
    if not reset:
        return
    remaining = headers.get('X-RateLimit-Remaining')
    limit = headers.get('X-RateLimit-Limit')
    delta = datetime.fromtimestamp(int(reset)) - datetime.now()
    logger.debug('{}/{} resets in {} min'.format(
        remaining, limit, str(delta.total_seconds() / 60).split('.')[0]))


def is_ssl_error(exception):
    """ return True if exception is SSLError or ProxyError, False otherwise
    """
    logger.debug('checking exception for retry candidacy')
    if isinstance(exception, SSLError):
        logger.info('SSLError encountered - retrying request in a few seconds')
        return True
    if isinstance(exception, ProxyError):
        logger.info('ProxyError encountered - retrying request in a few seconds')
        return True
    return False


def is_403_error(exception):
    """ return True if exception is 403 HTTPError, False otherwise
    """
    logger.debug('checking exception for retry candidacy')
    if isinstance(exception, HTTPError):
        if exception.response.status_code == 403:
            logger.info('HTTPError 403 encountered - retrying request in 60 seconds')
            return True
    return False


def get_resource_id(endpoint):
    """ return resource id from endpoint
    """
    return endpoint.split('/')[-1]


def get_resource(endpoint, index=-2):
    """ return resource from endpoint
    """
    return endpoint.split('/')[index][:-1]


def get_owner_repo(endpoint):
    """ return owner repo from endpoint
    """
    return '/'.join(endpoint.split('/')[2:4])


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


def search(items, key, value):
    """ return item in items whose key equals value
    """
    for item in items:
        if item[key] == value:
            return item


class GitHubAPI(RESTclient):

    def __init__(self, hostname, **kwargs):
        logger.debug('executing GitHubAPI constructor')
        if not kwargs.get('bearer_token'):
            raise ValueError('bearer_token must be provided')
        super(GitHubAPI, self).__init__(hostname, **kwargs)

    def process_response(self, response, **kwargs):
        """ subclass override to including logging of ratelimits
        """
        log_ratelimit(response.headers)
        return super(GitHubAPI, self).process_response(response, **kwargs)

    def get_headers(self, **kwargs):
        """ return headers to pass to requests method
        """
        headers = super(GitHubAPI, self).get_headers(**kwargs)
        headers['Accept'] = 'application/vnd.github.v3+json'
        return headers

    def get_next_endpoint(self, link_header):
        """ return next endpoint from link header
        """
        if not link_header:
            logger.debug('link header is empty')
            return
        regex = r".*<https://{}(?P<endpoint>/.*?)>; rel=\"next\".*".format(self.hostname)
        match = re.match(regex, link_header)
        if match:
            endpoint = match.group('endpoint')
            logger.debug('found next endpoint in link header: {}'.format(endpoint))
            return endpoint
        logger.debug('next endpoints not found in link header')

    def read_all(self, endpoint):
        """ get all items from endpoint - respects paging
        """
        logger.debug('get items from: {}'.format(endpoint))
        items = []
        while True:
            response = self.ratelimit_request(self.get, endpoint, raw_response=True)
            link_header = None
            if response:
                data = response.json()
                if isinstance(data, list):
                    items.extend(response.json())
                else:
                    items.append(data)
                link_header = response.headers.get('Link')

            endpoint = self.get_next_endpoint(link_header)
            if not endpoint:
                logger.debug('no more pages to retrieve')
                break

        return items

    def read(self, endpoint, attributes=None):
        """ return list of resources retrieved from endpoint with filtered attributes
        """
        items = self.read_all(endpoint)
        return match_keys(items, attributes)

    def get_repos(self, organization=None, user=None, regex='', blacklist_repos=None, **attributes):
        """ return organization repos that match the provided attributes
        """
        if not blacklist_repos:
            blacklist_repos = []
        endpoint = '/orgs/{}/repos'.format(organization)
        if user:
            endpoint = '/users/{}/repos'.format(user)
        repos = self.read_all(endpoint)
        if not regex and not attributes:
            return repos
        matched_repos = match_key_values(repos, regex=regex, **attributes)
        return [repo['name'] for repo in matched_repos if repo['name'] not in blacklist_repos]

    def get_labels(self, repo):
        """ return labels contained in repo
            repo must be formatted as ':owner/:repo'
            GET /repos/:owner/:repo/labels
        """
        return self.read(
            '/repos/{}/labels'.format(repo),
            attributes=[
                'name',
                'description',
                'color'
            ])

    def get_milestones(self, repo):
        """ return milestones contained in repo
            repo must be formatted as ':owner/:repo'
            GET /repos/:owner/:repo/milestones
        """
        return self.read(
            '/repos/{}/milestones'.format(repo),
            attributes=[
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
            self.ratelimit_request(self.get, endpoint, raw_response=True)
            return True
        except HTTPError as exception:
            if exception.response.status_code == 404:
                return False
            raise exception

    def modify(self, endpoint, payload, resource_id=None, noop=False):
        """ modify resource using PATCH endpoint
        """
        self.ratelimit_request(self.patch, endpoint, json=payload, noop=noop)
        resource_id = resource_id if resource_id else get_resource_id(endpoint)
        logger.info("modified {} '{}' in repo '{}' - NOOP: {}".format(
            get_resource(endpoint), resource_id, get_owner_repo(endpoint), noop))

    def create(self, endpoint, payload, resource_id, noop=False):
        """ create resource using POST endpoint
        """
        self.ratelimit_request(self.post, endpoint, json=payload, noop=noop)
        logger.info("created {} '{}' in repo '{}' - NOOP: {}".format(
            get_resource(endpoint, index=-1), payload.get(resource_id), get_owner_repo(endpoint), noop))

    def sync_labels(self, repo, labels, source_repo, modified_since=None, noop=True):
        """ sync labels to repo
            repo must be formatted as ':owner/:repo'
        """
        logger.info("synchronizing {} labels to repo '{}'".format(len(labels), repo))
        endpoint = '/repos/{}/labels'.format(repo)
        for label in labels:
            name = label['name']
            label_endpoint = '{}/{}'.format(endpoint, name)
            source_endpoint = '/repos/{}/labels/{}'.format(source_repo, name)
            if self.exists(label_endpoint):
                if self.modified_since(source_endpoint, modified_since):
                    self.modify(label_endpoint, label, noop=noop)
                else:
                    logger.info("label '{}' in repo '{}' has not been modified since '{}'".format(name, repo, modified_since))
            else:
                self.create(endpoint, label, 'name', noop=noop)
        logger.info('')

    def sync_milestones(self, repo, milestones, source_repo, modified_since=None, noop=True):
        """ sync milestones to repo
            repo must be formatted as ':owner/:repo'
        """
        logger.info("synchronizing {} milestones to repo '{}'".format(len(milestones), repo))
        repo_milestones = self.get_milestones(repo)
        endpoint = '/repos/{}/milestones'.format(repo)
        for milestone in milestones:
            repo_milestone = search(repo_milestones, 'title', milestone['title'])
            if repo_milestone:
                source_endpoint = '/repos/{}/milestones/{}'.format(source_repo, milestone.pop('number'))
                if self.modified_since(source_endpoint, modified_since):
                    target_endpoint = '{}/{}'.format(endpoint, repo_milestone['number'])
                    self.modify(target_endpoint, milestone, resource_id=milestone['title'], noop=noop)
                else:
                    logger.info("milestone '{}' has not been modified since '{}'".format(milestone['title'], modified_since))
            else:
                milestone.pop('number')
                sanitized_milestone = {key: value for key, value in milestone.items() if value is not None}
                self.create(endpoint, sanitized_milestone, 'title', noop=noop)
        logger.info('')

    def sync_repos(self, source_repo, organization=None, user=None, regex='', blacklist_repos=None, modified_since=None, noop=False):
        """ sync labels and milestones in source_repo to all matching repos in organization or user
        """
        owner = organization if organization else user
        repos = self.get_repos(organization=organization, user=user, regex=regex, blacklist_repos=blacklist_repos, archived=False, disasbled=False)
        logger.info("retrieved {} repos in '{}'".format(len(repos), owner))

        labels = self.get_labels(source_repo)
        logger.info("retrieved {} labels from label repo '{}'".format(len(labels), source_repo))

        milestones = self.get_milestones(source_repo)
        logger.info('retrieved {} milestones from {}'.format(len(milestones), source_repo))

        for repo in repos:
            repo_name = '{}/{}'.format(owner, repo)
            self.sync_labels(repo_name, labels, source_repo, noop=noop)
            self.sync_milestones(repo_name, milestones, source_repo, noop=noop)

    @retry(retry_on_exception=is_ssl_error, wait_random_min=10000, wait_random_max=20000, stop_max_attempt_number=3)
    def modified_since(self, endpoint, modified_since):
        """ return True if endpoint has been modified since modified_since
        """
        if not modified_since:
            return True
        response = self.get(
            endpoint,
            raw_response=True,
            headers={
                'If-Modified-Since': modified_since
            })
        return response.status_code == 200

    @retry(retry_on_exception=is_ssl_error, wait_random_min=10000, wait_random_max=20000, stop_max_attempt_number=3)
    @retry(retry_on_exception=is_403_error, wait_fixed=60000, stop_max_attempt_number=60)
    @sleep_and_retry
    @limits(calls=60, period=60)
    def ratelimit_request(self, function, *args, **kwargs):
        """ provides a method to funnel ratelimit requests
        """
        raw_response = kwargs.get('raw_response', False)
        response = function(*args, **kwargs)
        if raw_response:
            response.raise_for_status()
        return response

    @classmethod
    def get_client(self):
        """ return instance of GitHubAPI
        """
        return GitHubAPI(
            getenv('GH_BASE_URL', HOSTNAME),
            bearer_token=getenv('GH_TOKEN_PSW'))

    # def create_test_repos(self, count):
    #     for index in range(count):
    #         count = index + 1
    #         name = 'test_us6379-{}'.format(str(count).zfill(2))
    #         self.post('/user/repos', json={'name': name})
    #         print('created repo: {}'.format(name))

    # def delete_test_repos(self, user):
    #     repos = self.get_repos(user=user)
    #     for repo in repos:
    #         repo_name = repo['name']
    #         if 'test_us6379-' in repo_name:
    #             self.delete('/repos/{}/{}'.format(user, repo_name))
    #             print('deleted repo: {}'.format(repo_name))
