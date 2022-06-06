import re
import json
import logging
import argparse
from os import getenv
from time import sleep
from rest3client import RESTclient
from github3api import GitHubAPI
from mp4ansi import MP4ansi
from mdutils import MdUtils
from requests.exceptions import HTTPError
from prepbadge.github import get_client as get_github_client
from prepbadge.github import create_pull_request_workflow

logger = logging.getLogger(__name__)


CODECOV_HOST = 'codecov.io'
JENKINS_HOST = 'jenkins.edgexfoundry.org'
DEVOPS_REPOS = ['edgex-global-pipelines', 'cd-management', 'ci-management', 'ci-build-images', 'sample-service', 'jenkins_pipeline_presentation']
LOCAL_BRANCH = 'US149'


def get_parser():
    """ return argument parser
    """
    parser = argparse.ArgumentParser(
        description='A Python script that creates multiple pull request workflows to update a target organization repos with badges')
    parser.add_argument(
        '--org',
        dest='org',
        type=str,
        default=getenv('GH_ORG'),
        required=False,
        help='GitHub organization containing repos to process')
    parser.add_argument(
        '--repos',
        dest='repos_regex',
        type=str,
        default=None,
        required=False,
        help='a regex to match name of repos to include for processing, if not specified then all non-archived, non-disabled repos in org will be processed')
    parser.add_argument(
        '--branch',
        dest='local_branch',
        type=str,
        default=LOCAL_BRANCH,
        required=False,
        help='the name of the local branch to create in your fork that will contain your changes')
    parser.add_argument(
        '--execute',
        dest='execute',
        action='store_true',
        help='execute processing - not setting is same as running in NOOP mode')
    return parser


def configure_logging():
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('prepbadge.log')
    file_formatter = logging.Formatter("%(asctime)s %(processName)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    rootLogger.addHandler(file_handler)


def get_github_data(*args):
    """ return non-archived and non-disabled github repos for owner
    """
    owner = args[0]['owner']
    logger.debug(f'getting github information for {owner} repos')
    repos = []
    client, _ = get_github_client()
    repo_attributes = {'archived': False, 'disabled': False}
    total_repos = client.total(f'/orgs/{owner}/repos')
    logger.debug(f'{owner} has a total of {total_repos} matching repos in github')
    for page in client.get(f'/orgs/{owner}/repos', _get='page'):
        for repo in page:
            logger.debug(f"checking repo {repo['name']}")
            sleep(.02)
            match_attributes = all(repo[key] == value for key, value in repo_attributes.items() if key in repo)
            if match_attributes:
                logger.debug(f"checking language for {repo['name']}")
                languages = client.get(repo['languages_url'].replace(f'https://{client.hostname}', ''))
                logger.debug(f"checking tags for {repo['name']}")
                tags = client.get(repo['tags_url'].replace(f'https://{client.hostname}', ''))
                item = {
                    'name': repo['name'],
                    'owner_repo': repo['full_name'],
                    'default_branch': repo['default_branch'],
                    'github_location': repo['html_url'].replace('https://', ''),
                    'github_url': repo['html_url'],
                    'is_go_based': 'Go' in languages,
                    'has_license': not repo['license'] is None,
                    'has_tags': len(tags) > 1,
                    'team_members_url': f"https://github.com/orgs/{owner}/teams/{repo['name']}-committers/members"
                }
                if repo['name'] in DEVOPS_REPOS:
                    item['team_members_url'] = f'https://github.com/orgs/{owner}/teams/devops-core-team/members'
                repos.append(item)
    return repos


def get_codecov_client():
    """ return instance of RESTclient for codecov.io
    """
    token = getenv('CC_TOKEN_PSW')
    if not token:
        raise ValueError('CC_TOKEN_PSW environment variable must be set to token')
    return RESTclient(CODECOV_HOST, token=token, retries=[{'wait_fixed': 5000, 'stop_max_attempt_number': 3}])


def get_codecov_data(*args):
    """ get codecov data
    """
    owner = args[0]['owner']
    logger.debug(f'getting codecov information for {owner} repos')
    data = []
    client = get_codecov_client()
    repos = client.get(f'/api/gh/{owner}?limit=100')['repos']
    logger.debug(f'{owner} has a total of {len(repos)} repos registered in codecov.io')
    for repo in repos:
        logger.debug(f"retrieving codecov data for {repo['name']} repo")
        try:
            settings = client.get(f"/api/gh/{owner}/{repo['name']}/settings")
        except HTTPError as exception:
            logger.warn(exception)
            continue
        data.append({
            'repo': repo['name'],
            'codecov_coverage': repo['coverage'],
            'codecov_badge': f"https://{client.hostname}/gh/{owner}/{repo['name']}/branch/main/graph/badge.svg?token={settings['repo']['image_token']}",
            'codecov_url': f"https://codecov.io/gh/{owner}/{repo['name']}"
        })
    return data


def get_jenkins_client():
    """ return instance of RESTclient for jenkins api
    """
    user = getenv('JN_TOKEN_USR')
    if not user:
        raise ValueError('JN_TOKEN_USR environment variable must be set to token')
    password = getenv('JN_TOKEN_PSW')
    if not password:
        raise ValueError('JN_TOKEN_PSW environment variable must be set to token')
    return RESTclient(JENKINS_HOST, user=user, password=password)


def get_jenkins_data(*args):
    """ return jenkins data for owner
    """
    owner = args[0]['owner']
    logger.debug(f'getting jenkins information for {owner} repos')
    data = []
    client = get_jenkins_client()
    jobs = client.get(f'/job/{owner}/api/json?tree=displayName,name,url,jobs[name,url,jobs[name,url,buildable]]')
    logger.debug(f"{owner} has a total of {len(jobs['jobs'])} repos registered in jenkins")
    display_name = jobs['displayName']
    for job in jobs['jobs']:
        sleep(.1)
        repo = job['name']
        logger.debug(f"retrieving jenkins data for {repo} repo")
        index = find(job['jobs'], 'main')
        if index > -1:
            data.append({
                'repo': repo,
                'jenkins_badge': f'https://{JENKINS_HOST}/view/{display_name}/job/{owner}/job/{repo}/job/main/badge/icon'.replace(" ", "%20"),
                'jenkins_url': f'https://{JENKINS_HOST}/view/{display_name}/job/{owner}/job/{repo}/job/main/'.replace(" ", "%20")
            })
    return data


def write_file(process_data, name):
    """ write data to json file
    """
    filename = f'{name}.json'
    with open(filename, 'w') as fp:
        json.dump(process_data, fp, indent=2)
        print(f'{name} report written to {filename}')


def find(items, name):
    """ return index of item with name in items
    """
    for index, item in enumerate(items):
        if item['name'] == name:
            return index
    logger.warn(f'no item with name {name} in target list')
    return -1


def coalesce_data(github, codecov, jenkins):
    """ coalesce repos from codecov and jenkins into github
    """
    for item in codecov[0]['result']:
        repo = item.pop('repo')
        index = find(github[0]['result'], repo)
        if index > -1:
            github[0]['result'][index].update(item)
    for item in jenkins[0]['result']:
        repo = item.pop('repo')
        index = find(github[0]['result'], repo)
        if index > -1:
            github[0]['result'][index].update(item)
    # write_file(github, 'badges')


def create_markdown(github, owner):
    """ create markdown for repos in github dict
    """
    filename = 'prepbadge'
    print(f'Creating markdown file for {owner} repos in {filename}.md')
    md = MdUtils(file_name=filename, title='EdgeXFoundry Repo Badges Preview')
    for repo in github[0]['result']:
        md.new_header(level=1, title=md.new_inline_link(link=repo['github_url'], text=repo['name']))
        for badge in repo['badges']:
            md.write(text=f'{badge} ', wrap_width=0)
        md.new_line('')
    md.create_md_file()


def add_badges(github, owner):
    """ add badge data to github dict
    """
    print(f'Adding badges for {owner} repos')
    for repo in github[0]['result']:
        repo['badges'] = []
        if 'jenkins_badge' in repo:
            repo['badges'].append(f"[![Build Status]({repo['jenkins_badge']})]({repo['jenkins_url']})")
        if 'codecov_badge' in repo:
            repo['badges'].append(f"[![Code Coverage]({repo['codecov_badge']})]({repo['codecov_url']})")
        if repo['is_go_based']:
            repo['badges'].append(f"[![Go Report Card](https://goreportcard.com/badge/{repo['github_location']})](https://goreportcard.com/report/{repo['github_location']})")
        if repo['has_tags']:
            repo['badges'].append(f"[![GitHub Latest Dev Tag)](https://img.shields.io/github/v/tag/{repo['owner_repo']}?include_prereleases&sort=semver&label=latest-dev)]({repo['github_url']}/tags)")
            repo['badges'].append(f"![GitHub Latest Stable Tag)](https://img.shields.io/github/v/tag/{repo['owner_repo']}?sort=semver&label=latest-stable)")
        if repo['has_license']:
            repo['badges'].append(f"[![GitHub License](https://img.shields.io/github/license/{repo['owner_repo']})](https://choosealicense.com/licenses/apache-2.0/)")
        if repo['is_go_based']:
            repo['badges'].append(f"![GitHub go.mod Go version](https://img.shields.io/github/go-mod/go-version/{repo['owner_repo']})")
        repo['badges'].append(f"[![GitHub Pull Requests](https://img.shields.io/github/issues-pr-raw/{repo['owner_repo']})]({repo['github_url']}/pulls)")
        repo['badges'].append(f"[![GitHub Contributors](https://img.shields.io/github/contributors/{repo['owner_repo']})]({repo['github_url']}/contributors)")
        repo['badges'].append(f"[![GitHub Committers](https://img.shields.io/badge/team-committers-green)]({repo['team_members_url']})")
        repo['badges'].append(f"[![GitHub Commit Activity](https://img.shields.io/github/commit-activity/m/{repo['owner_repo']})]({repo['github_url']}/commits)")
    # write_file(github, 'badges')


def run_github_data_collection(owner):
    """ run github data collection
    """
    print(f'Retrieving github repos for {owner} ...')
    process_data = [{'owner': owner}]
    MP4ansi(
        function=get_github_data,
        process_data=process_data,
        config={
            'id_regex': r'^getting github information for (?P<value>.*) repos$',
            'progress_bar': {
                'total': r'^.* has a total of (?P<value>\d+) matching repos in github$',
                'count_regex': r'^checking repo (?P<value>.*)$',
                'progress_message': 'Retrieval of github.com repos complete'
            }
        }).execute(raise_if_error=True)
    return process_data


def run_codecov_data_collection(owner):
    """ run codecov data collection
    """
    print(f'Retrieving codecov.io data for {owner} ...')
    process_data = [{'owner': owner}]
    MP4ansi(
        function=get_codecov_data,
        process_data=process_data,
        config={
            'id_regex': r'^getting codecov information for (?P<value>.*) repos$',
            'progress_bar': {
                'total': r'^.* has a total of (?P<value>\d+) repos registered in codecov.io$',
                'count_regex': r'^retrieving codecov data for (?P<value>.*) repo$',
                'progress_message': 'Retrieval of codecov.io data complete'
            }
        }).execute(raise_if_error=True)
    return process_data


def run_jenkins_data_collection(owner):
    """ run jenkins data collection
    """
    print(f'Retrieving jenkins data for {owner} ...')
    process_data = [{'owner': owner}]
    MP4ansi(
        function=get_jenkins_data,
        process_data=process_data,
        config={
            'id_regex': r'^getting jenkins information for (?P<value>.*) repos$',
            'progress_bar': {
                'total': r'^.* has a total of (?P<value>\d+) repos registered in jenkins$',
                'count_regex': r'^retrieving jenkins data for (?P<value>.*) repo$',
                'progress_message': 'Retrieval of jenkins data complete'
            }
        }).execute(raise_if_error=True)
    return process_data


def get_process_data_for_pull_request_workflows(repos_data, repos_regex, local_branch, noop):
    """ return process data for pull request workflows
    """
    logger.debug('getting process data for pull request workflows')
    if repos_regex is None:
        repos_regex = ''
    process_data = []
    for repo_data in repos_data:
        match = re.match(repos_regex, repo_data['name'])
        if match:
            item = {
                'owner_repo': repo_data['owner_repo'],
                'default_branch': repo_data['default_branch'],
                'local_branch': local_branch,
                'badges': repo_data['badges'],
                'reviewers': ['bill-mahoney', 'ernestojeda', 'jamesrgregg', 'cjoyv'],
                # 'reviewers': [],
                'labels': ['documentation'],
                'milestone': 'Kamakura',
                'noop': noop
            }
            process_data.append(item)
    return process_data


def run_create_pull_request_workflows(owner, repos_data, repos_regex, local_branch, noop):
    """ execute pull request workflow
    """
    print(f'Executing pull request workflows for {owner} ...')
    process_data = get_process_data_for_pull_request_workflows(repos_data, repos_regex, local_branch, noop)
    if not process_data:
        print('Nothing to execute')
        return
    MP4ansi(
        function=create_pull_request_workflow,
        process_data=process_data,
        config={
            'id_regex': fr'^creating pull request workflow for {owner}/(?P<value>.*) - noop: .*$',
            'id_justify': True,
            'id_width': 23,
            'progress_bar': {
                'total': r'^pull request workflow has a total of (?P<value>\d+) steps$',
                'count_regex': r'^executing step (?P<value>-) .*$',
                'progress_message': 'Pull request workflow complete'
            }
        }).execute(raise_if_error=True)


def main():
    """ main function
    """
    args = get_parser().parse_args()
    configure_logging()
    github_data = run_github_data_collection(args.org)
    codecov_data = run_codecov_data_collection(args.org)
    jenkins_data = run_jenkins_data_collection(args.org)
    coalesce_data(github_data, codecov_data, jenkins_data)
    add_badges(github_data, args.org)
    create_markdown(github_data, args.org)
    run_create_pull_request_workflows(args.org, github_data[0]['result'], args.repos_regex, args.local_branch, not args.execute)


if __name__ == '__main__':
    main()
