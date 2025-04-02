
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
from os import getenv
from time import sleep
from datetime import datetime

from requests.exceptions import SSLError
from requests.exceptions import ProxyError
from requests.exceptions import ConnectionError
from semantic_version import Version
from semantic_version import SimpleSpec
from semantic_version import validate as validate_version
from github3api import GitHubAPI


logger = logging.getLogger(__name__)


class API(GitHubAPI):

    def __init__(self, **kwargs):
        logger.debug('executing API constructor')

        if not kwargs.get('bearer_token'):
            raise ValueError('bearer_token must be provided')

        super(API, self).__init__(**kwargs)

    def get_repos(self, organization=None, user=None, include=None, exclude=None, **attributes):
        """ return organization repos that match the provided attributes
        """
        endpoint = f'/orgs/{organization}/repos'
        owner = organization
        if user:
            endpoint = f'/users/{user}/repos'
            owner = user
        repos = self.get(endpoint, _get='all')
        return API.match_repos(
            repos=repos,
            owner=owner,
            include=include,
            exclude=exclude,
            **attributes)

    def get_latest_version(self, repo=None, tags=None, branch=None):
        """ return latest version and associated commit sha from repo tags
        """
        if not branch:
            branch = 'main'
        for page in self.get(f'/repos/{repo}/commits?sha={branch}', _get='page'):
            logger.debug(f'getting commits for repo {page}')
            for commit in page:
                commit_sha = commit['sha']
                tag = API.lookup_tag(tags=tags, sha=commit_sha)
                if tag:
                    version = API.get_version(name=tag['name'])
                    if version:
                        return (version, commit_sha)
        return (None, None)

    def get_prerelease_tags(self, repo=None, branch=None):
        """ return prerelease tags, latest version and latest version sha for repo
        """
        logger.debug(f'getting prerelease tags for repo {repo}')
        tags = self.get(f'/repos/{repo}/tags', _get='all')
        if not tags:
            logger.info(f'repo {repo} has no tags')
            return
        latest_version, latest_version_sha = self.get_latest_version(repo=repo, tags=tags, branch=branch)
        if not latest_version:
            logger.info(f'repo {repo} has no tags that are versions')
            return
        logger.debug(f'repo {repo} latest tag version is {latest_version}')
        exclude = latest_version
        prerelease_tags = API.filter_prerelease_tags(tags=tags, exclude=exclude)
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
                self.delete(endpoint, noop=noop)
                if noop:
                    sleep(.30)
                logger.info(f'removed tag {prerelease_tag} from repo {repo} - NOOP: {noop}')
            except Exception as exception:
                logger.error(f'error occurred removing tag {prerelease_tag} from repo {repo}: {exception}')
        logger.debug(f'removed prerelease tags from repo {repo}')

    def get_version_tags(self, repo=None, branch=None, expression=None):
        """ return version tags, latest version and latest version sha for repo
        """
        logger.info(f'getting version tags for repo {repo}')
        tags = self.get(f'/repos/{repo}/tags', _get='all')
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
        version_tags = API.filter_version_tags(tags=tags, exclude=exclude, expression=expression)
        return version_tags, latest_version, latest_version_sha

    def remove_version_tags(self, repo=None, branch=None, noop=True, expression=None):
        """ remove version tags from repo
        """
        logger.info(f'removing version tags from repo {repo}')
        version_tags_result = self.get_version_tags(repo=repo, branch=branch, expression=expression)
        if version_tags_result is None:
            return
        version_tags = version_tags_result[0]
        logger.debug(f'repo {repo} has {str(len(version_tags)).zfill(3)} version tags that can be removed according to "{expression}"')
        for version_tag, _ in version_tags:
            try:
                endpoint = f'/repos/{repo}/git/refs/tags/{version_tag}'
                self.delete(endpoint, noop=noop)
                if noop:
                    sleep(.30)
                logger.info(f'removed tag {version_tag} from repo {repo} - NOOP: {noop}')
            except Exception as exception:
                logger.error(f'error occurred removing tag {version_tag} from repo {repo}: {exception}')
        logger.info(f'removed version tags from repo {repo}')

    def get_version_tags_report(self, repos=None, expression=None):
        """ get version tags report for repos
        """
        report = {}
        for repo in repos:
            version_tags_result = self.get_version_tags(repo=repo, expression=expression)
            if version_tags_result is None:
                report.update({f'{repo}': {}})
            else:
                report.update(
                    API.generate_version_report(
                        repo=repo,
                        version_tags=version_tags_result[0],
                        latest_version=version_tags_result[1],
                        latest_version_sha=version_tags_result[2]))
        return report

    def get_prerelease_tags_report(self, repos=None, branch=None):
        """ get prerelease tags report for repos
        """
        report = {}
        for repo in repos:
            prerelease_tags_result = self.get_prerelease_tags(repo=repo, branch=branch)
            if prerelease_tags_result is None:
                report.update({f'{repo}': {}})
            else:
                report.update(
                    API.generate_preprelease_report(
                        repo=repo,
                        prerelease_tags=prerelease_tags_result[0],
                        latest_version=prerelease_tags_result[1],
                        latest_version_sha=prerelease_tags_result[2]))
        return report

    @staticmethod
    def match_repos(*, repos, owner, include, exclude, **attributes):
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

    @staticmethod
    def lookup_tag(*, tags, sha):
        """ return tag with sha from tags
        """
        for tag in tags:
            if tag['commit']['sha'] == sha:
                return tag

    @staticmethod
    def filter_prerelease_tags(*, tags, exclude):
        """ return list of tags that are prereleases
        """
        prerelease_tags = []
        for tag in tags:
            tag_name = tag['name']
            tag_sha = tag['commit']['sha']
            version = API.get_version(name=tag_name)
            if version:
                if version.prerelease != ():
                    if exclude:
                        if (version.major, version.minor, version.patch) > (exclude.major, exclude.minor, exclude.patch):
                            logger.debug(f'excluding current prerelease version {version}')
                            continue
                    prerelease_tags.append((tag_name, tag_sha))
        return prerelease_tags

    @staticmethod
    def filter_version_tags(*, tags, exclude, expression):
        """ return list of tags that match expression
        """
        version_tags = []
        version_spec = SimpleSpec(expression)
        for tag in tags:
            tag_name = tag['name']
            tag_sha = tag['commit']['sha']
            version = API.get_version(name=tag_name)
            if version is not None:
                if version_spec.match(version):
                    version_tags.append((tag_name, tag_sha))
        return version_tags

    @staticmethod
    def get_version(*, name):
        """ return semantic version for name
        """
        if name.startswith('v'):
            name = name[1:]
        if not validate_version(name):
            logger.debug(f'{name} is not a valid semantic version')
            return
        return Version(name)

    @staticmethod
    def generate_preprelease_report(*, repo, prerelease_tags, latest_version, latest_version_sha):
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
            version = API.get_version(name=prerelease_tag)
            report[repo]['prerelease_tags'].append(
                (f'v{str(version)}', prerelease_sha))
        return report

    @staticmethod
    def generate_version_report(*, repo, version_tags, latest_version, latest_version_sha):
        """ generate version tag report for repo
        """
        report = {
            f'{repo}': {
                'latest_version': (str(latest_version), latest_version_sha),
                'version_tags_count': len(version_tags),
                'version_tags': []
            }
        }
        for version_tag, version_sha in version_tags:
            version = API.get_version(name=version_tag)
            report[repo]['version_tags'].append(
                (f'v{str(version)}', version_sha))
        return report

    @staticmethod
    def log_ratelimit(ratelimit):
        """ log rate limit data - override of base class
        """
        logger.info(f"{ratelimit['remaining']}/{ratelimit['limit']} resets in {ratelimit['minutes']} min")

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
