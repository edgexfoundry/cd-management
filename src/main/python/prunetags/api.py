
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
from requests.exceptions import ConnectionError
from retrying import retry
from datetime import datetime
from semantic_version import Version
from semantic_version import SimpleSpec
from semantic_version import validate as validate_version
from time import sleep

import logging
logger = logging.getLogger(__name__)

logging.getLogger('urllib3.connectionpool').setLevel(logging.CRITICAL)

HOSTNAME = 'api.github.com'


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


def is_connection_error(exception):
    """ return True if exception is SSLError, ProxyError or ConnectError, False otherwise
    """
    logger.debug(f'checking exception for retry candidacy: {exception}')

    if isinstance(exception, SSLError):
        logger.info('SSLError encountered - retrying request in a few seconds')
        return True
    if isinstance(exception, ProxyError):
        logger.info('ProxyError encountered - retrying request in a few seconds')
        return True
    if isinstance(exception, ConnectionError):
        logger.info('ConnectionError encountered - retrying request in a few seconds')
        return True
    return False


def is_ratelimit_error(exception):
    """ return True if exception is 403 HTTPError, False otherwise
    """
    logger.debug('checking exception for retry candidacy')
    if isinstance(exception, HTTPError):
        if exception.response.status_code == 403:
            logger.info('HTTPError 403 encountered - retrying request in 60 seconds')
            return True
    return False


class GitHubAPI(RESTclient):

    def __init__(self, hostname, **kwargs):
        logger.debug('executing GitHubAPI constructor')
        if not kwargs.get('bearer_token'):
            raise ValueError('bearer_token must be provided')
        super(GitHubAPI, self).__init__(hostname, **kwargs)

    def get_response(self, response, **kwargs):
        """ subclass override to including logging of ratelimits
        """
        GitHubAPI.log_ratelimit(response.headers)
        return super(GitHubAPI, self).get_response(response, **kwargs)

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
        regex = fr".*<https://{self.hostname}(?P<endpoint>/.*?)>; rel=\"next\".*"
        match = re.match(regex, link_header)
        if match:
            endpoint = match.group('endpoint')
            logger.debug(f'found next endpoint in link header: {endpoint}')
            return endpoint
        logger.debug('next endpoints not found in link header')

    def read_all(self, endpoint):
        """ get all items from endpoint - respects paging
        """
        logger.debug(f'get items from: {endpoint}')
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

    def read_page(self, endpoint):
        """ generator that yields pages from endpoint
        """
        while True:
            response = self.ratelimit_request(self.get, endpoint, raw_response=True)
            for page in response.json():
                yield page
            endpoint = self.get_next_endpoint(response.headers.get('Link'))
            if not endpoint:
                logger.debug('no more pages')
                break

    def get_repos(self, organization=None, user=None, include=None, exclude=None, **attributes):
        """ return organization repos that match the provided attributes
        """
        endpoint = f'/orgs/{organization}/repos'
        owner = organization
        if user:
            endpoint = f'/users/{user}/repos'
            owner = user
        repos = self.read_all(endpoint)
        return GitHubAPI.match_repos(
            repos=repos,
            owner=owner,
            include=include,
            exclude=exclude,
            **attributes)

    def get_latest_version(self, repo=None, tags=None, branch=None):
        """ return latest version and associated commit sha from repo tags
        """
        if not branch:
            branch = 'master'
        for commit in self.read_page(f'/repos/{repo}/commits?sha={branch}'):
            commit_sha = commit['sha']
            tag = GitHubAPI.lookup_tag(tags=tags, sha=commit_sha)
            if tag:
                version = GitHubAPI.get_version(name=tag['name'])
                if version:
                    return (version, commit_sha)
        return (None, None)

    def get_prerelease_tags(self, repo=None, branch=None):
        """ return prerelease tags, latest version and latest version sha for repo
        """
        logger.debug(f'getting prerelease tags for repo {repo}')
        tags = self.read_all(f'/repos/{repo}/tags')
        if not tags:
            logger.info(f'repo {repo} has no tags')
            return
        latest_version, latest_version_sha = self.get_latest_version(repo=repo, tags=tags, branch=branch)
        if not latest_version:
            logger.info(f'repo {repo} has no tags that are versions')
            return
        logger.debug(f'repo {repo} latest tag version is {latest_version}')
        exclude = None
        if latest_version.prerelease != ():
            exclude = latest_version
        prerelease_tags = GitHubAPI.filter_prerelease_tags(tags=tags, exclude=exclude)
        logger.debug(f'repo {repo} has {str(len(prerelease_tags)).zfill(3)} prerelease tags')
        return prerelease_tags, latest_version, latest_version_sha

    def remove_prerelease_tags(self, repo=None, branch=None, noop=True):
        """ remove prerelease tags from repo
        """
        logger.info(f'removing prerelease tags from repo {repo}')
        prerelease_tags_result = self.get_prerelease_tags(repo=repo, branch=branch)
        if prerelease_tags_result is None:
            return
        prerelease_tags = prerelease_tags_result[0]
        logger.debug(f'repo {repo} has {str(len(prerelease_tags)).zfill(3)} prerelease tags that can be removed')
        for prerelease_tag, _ in prerelease_tags:
            try:
                endpoint = f'/repos/{repo}/git/refs/tags/{prerelease_tag}'
                self.ratelimit_request(self.delete, endpoint, noop=noop)
                if noop:
                    sleep(.30)
                logger.info(f'removed tag {prerelease_tag} from repo {repo} - NOOP: {noop}')
            except Exception as exception:
                logger.error(f'error occurred removing tag {prerelease_tag} from repo {repo}: {exception}')
        logger.debug(f'removed prerelease tags from repo {repo}')

    def get_prerelease_tags_report(self, repos=None):
        """ get prerelease tags report for repos
        """
        report = {}
        for repo in repos:
            prerelease_tags_result = self.get_prerelease_tags(repo=repo)
            if prerelease_tags_result is None:
                report.update({f'{repo}': {}})
            else:
                report.update(
                    GitHubAPI.generate_preprelease_report(
                        repo=repo,
                        prerelease_tags=prerelease_tags_result[0],
                        latest_version=prerelease_tags_result[1],
                        latest_version_sha=prerelease_tags_result[2]))
        return report

    @retry(retry_on_exception=is_connection_error, wait_random_min=10000, wait_random_max=20000, stop_max_attempt_number=6)
    @retry(retry_on_exception=is_ratelimit_error, wait_fixed=60000, stop_max_attempt_number=60)
    def ratelimit_request(self, function, *args, **kwargs):
        """ provides a method to funnel ratelimit requests
        """
        raw_response = kwargs.get('raw_response', False)
        response = function(*args, **kwargs)
        if raw_response:
            response.raise_for_status()
        return response

    @classmethod
    def match_repos(cls, *, repos, owner, include, exclude, **attributes):
        """ return list of repos whose name matches include and key values match attributes and name does not match exclude
        """
        match_include = True
        match_exclude = False
        matched = []
        for repo in repos:
            repo_name = repo['name']
            if include:
                match_include = re.match(include, repo_name)
            if exclude:
                match_exclude = re.match(exclude, repo_name)
            match_attributes = all(repo[key] == value for key, value in attributes.items() if key in repo)
            if match_include and match_attributes and not match_exclude:
                matched.append(f'{owner}/{repo_name}')
        return matched

    @classmethod
    def lookup_tag(cls, *, tags, sha):
        """ return tag with sha from tags
        """
        for tag in tags:
            if tag['commit']['sha'] == sha:
                return tag

    @classmethod
    def filter_prerelease_tags(cls, *, tags, exclude):
        """ return list of tags that are prereleases
        """
        prerelease_tags = []
        for tag in tags:
            tag_name = tag['name']
            tag_sha = tag['commit']['sha']
            version = GitHubAPI.get_version(name=tag_name)
            if version:
                if version.prerelease != ():
                    if exclude:
                        if f'{version.major}.{version.minor}.{version.patch}' == f'{exclude.major}.{exclude.minor}.{exclude.patch}':
                            logger.debug(f'excluding current prerelease version {version}')
                            continue
                    prerelease_tags.append((tag_name, tag_sha))
        return prerelease_tags

    @classmethod
    def get_version(cls, *, name):
        """ return semantic version for name
        """
        if name.startswith('v'):
            name = name[1:]
        if not validate_version(name):
            logger.debug(f'{name} is not a valid semantic version')
            return
        return Version(name)

    @classmethod
    def generate_preprelease_report(cls, *, repo, prerelease_tags, latest_version, latest_version_sha):
        """ generate prerelease tag report for repo
        """
        report = {
            f'{repo}': {
                'latest_version': (str(latest_version), latest_version_sha),
                'prerelease_tags_count': len(prerelease_tags),
                'prerelease_tags': []
            }
        }
        for prerelease_tag, prerelease_sha in prerelease_tags:
            version = GitHubAPI.get_version(name=prerelease_tag)
            report[repo]['prerelease_tags'].append(
                (f'v{str(version)}', prerelease_sha))
        return report

    @classmethod
    def log_ratelimit(cls, headers):
        """ convert and log rate limit data
        """
        reset = headers.get('X-RateLimit-Reset')
        if not reset:
            return
        remaining = headers.get('X-RateLimit-Remaining')
        limit = headers.get('X-RateLimit-Limit')
        delta = datetime.fromtimestamp(int(reset)) - datetime.now()
        minutes = str(delta.total_seconds() / 60).split('.')[0]
        logger.debug(f'{remaining}/{limit} resets in {minutes} min')

    @classmethod
    def get_client(cls):
        """ return instance of GitHubAPI
        """
        return GitHubAPI(
            getenv('GH_BASE_URL', HOSTNAME),
            bearer_token=getenv('GH_TOKEN_PSW'))
