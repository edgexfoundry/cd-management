import os
import re
import sys
import random
import inspect
import logging
import subprocess
from os import getenv
from time import sleep
from requests.exceptions import HTTPError
from functools import wraps

from github3api import GitHubAPI


logger = logging.getLogger(__name__)


class ForkExists(Exception):
    """ Raise when fork already exists
    """
    pass


class PullRequestExists(Exception):
    """ Raise when pull request already exists
    """
    pass


class PullRequestVerificationFailure(Exception):
    """ Raise when pull request verification fails
    """
    pass


class NotFound(Exception):
    """ Raise when something is expected but not found
    """
    pass


def workflow_step(function):
    """ wraps function as a workflow step
    """
    # @wraps(function)
    def _workflow_step(*args, **kwargs):
        """ internal decorator for workflow step
        """
        logger.debug(f'executing step - {function.__name__}')
        sleep(random.choice([.1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7, .75, .8, .85, .9, .95, 1]))
        # sleep(random.choice([.1, .15, .2, .25, .3, .35, .4, .45, .5]))
        return function(*args, **kwargs)

    return _workflow_step


def get_client():
    """ return instance of GitHubAPI RESTclient
    """
    token = getenv('GH_TOKEN_PSW')
    if not token:
        raise ValueError('GH_TOKEN_PSW environment variable must be set to token')
    client = GitHubAPI.get_client()
    user = client.get('/user')['login']
    return client, user


def fork_exists(client, owner_repo, user):
    """ return True if fork for owner_repo exists
    """
    exists = False
    response = None
    try:
        repo = owner_repo.split('/')[-1]
        response = client.get(f'/repos/{user}/{repo}')
        if response['fork'] and response['source']['full_name'] == owner_repo:
            exists = True

    except HTTPError:
        pass

    return exists


def get_fork(client, owner_repo, user):
    """ return fork object if fork for owner_repo exists
    """
    fork = None
    try:
        repo = owner_repo.split('/')[-1]
        response = client.get(f'/repos/{user}/{repo}')
        if response['fork'] and response['source']['full_name'] == owner_repo:
            fork = response

    except HTTPError:
        pass

    return fork


def find(items, key, value):
    """ return index, item tuple of item with key and value in list of dicts
    """
    for index, item in enumerate(items):
        if item[key] == value:
            return index, item
    raise NotFound(f'no item with {key} {value} in items')


def get_readme(working_dir):
    """ return tuple of readme.md path and boolean if it exists
    """
    filename = 'README.md'
    exists = False
    for file in os.listdir(working_dir):
        if file.lower() == 'readme.md':
            filename = file
            exists = True
    return f'{working_dir}/{filename}', exists


def finish_steps():
    """ log executing steps to update progress bar to completion
    """
    for _ in range(get_workflow_steps()):
        logger.debug('executing step - update progress bar to completion')
        sleep(0.1)


def execute_command(command, **kwargs):
    """ run command
    """
    # sleep(.1)
    working_dir = kwargs.get('cwd', '')
    logger.debug(f'{command} - ({working_dir})')
    arguments = kwargs
    arguments['stdout'] = subprocess.DEVNULL
    arguments['stderr'] = subprocess.DEVNULL
    subprocess.run(command, **arguments)


def get_workflow_steps():
    """ returns number of workflow steps in current module
    """
    def is_workflow_step(item):
        retdata = False
        if callable(item) and (item.__name__ == '_workflow_step'):
            retdata = True
        return retdata
    workflow_steps = inspect.getmembers(sys.modules[__name__], is_workflow_step)
    return len(workflow_steps)


@workflow_step
def check_pull_request(client, owner_repo, user, default_branch, local_branch):
    """ return True if open pull request exists
    """
    logger.debug(f'checking if pull request for {owner_repo} for {user}:{local_branch} exists or has been merged')
    # GitHub PR search appears to be broken
    # the following query: client.get("/repos/edgexfoundry/sample-service/pulls?state=all&base=master&head=soda480:US149")
    # returns nothing - when it should return something - there is a matching PR
    # thus refactored to do search page by page
    # response = client.get(f'/repos/{owner_repo}/pulls?state=all&head={user}:{local_branch}&base={default_branch}', _get='all')
    response = client.get(f'/repos/{owner_repo}/pulls?state=all&base={default_branch}&per_page=100', _get='all')
    # this was causing ERROR 403 Client Error - not retried for some reason
    # for page in client.get(f'/repos/{owner_repo}/pulls?state=all&base={default_branch}', _get='page'):
    for pr in response:
        if pr['head']['label'] == f'{user}:{local_branch}':
            state = pr['state']
            if state == 'open':
                raise PullRequestExists(f'{owner_repo} has an {state} pull request for {user}:{local_branch}')
            if state == 'closed':
                if pr['merged_at']:
                    raise PullRequestExists(f'{owner_repo} has a {state} and merged pull request for {user}:{local_branch}')


@workflow_step
def create_fork(client, owner_repo, user, sleep_time=None):
    """ create fork for owner repo for authenticated user
    """
    logger.debug(f'creating fork for {owner_repo}')

    fork = get_fork(client, owner_repo, user)
    if fork:
        response = fork
    else:
        if not sleep_time:
            sleep_time = 5

        response = client.post(f'/repos/{owner_repo}/forks')
        url = response['url'].replace(f'https://{client.hostname}', '')
        while True:
            try:
                client.get(url)
                logger.debug(f'fork for {owner_repo} has been created')
                break

            except HTTPError:
                logger.debug(f'fork for {owner_repo} is not yet ready')
                sleep(sleep_time)

    return response['name'], response['ssh_url'], response['source']['ssh_url']


@workflow_step
def create_working_dir(repo):
    """ execute command to create working directory and return it
    """
    working_dir = f"{getenv('PWD')}/github.com"
    execute_command(f'mkdir -p {working_dir}', shell=True)
    return working_dir


@workflow_step
def remove_clone_dir(working_dir, repo):
    """ execute command to remove working directory
    """
    execute_command(f'rm -rf {working_dir}/{repo}', shell=True)


@workflow_step
def clone_repo(working_dir, ssh_url):
    """ execute git clone
    """
    execute_command(f'git clone {ssh_url}', cwd=working_dir, shell=True)


@workflow_step
def add_remote_upstream(working_dir, source_ssh_url):
    """ add remote upstream
    """
    execute_command(f'git remote add upstream {source_ssh_url}', cwd=working_dir, shell=True)


@workflow_step
def rebase(working_dir, default_branch):
    """ rebase default branch
    """
    execute_command('git fetch upstream', cwd=working_dir, shell=True)
    execute_command(f'git rebase upstream/{default_branch}', cwd=working_dir, shell=True)
    execute_command(f'git push origin {default_branch}', cwd=working_dir, shell=True)


@workflow_step
def create_branch(working_dir, local_branch):
    """ create local branch from default branch
    """
    execute_command(f'git checkout -b {local_branch}', cwd=working_dir, shell=True)


@workflow_step
def update_readme(badges, repo, working_dir):
    """ update readme with badges
    """
    contents = []
    badges_to_add = []
    filename, exists = get_readme(working_dir)
    if exists:
        logger.debug(f'updating existing {filename}')
        with open(filename, 'r') as infile:
            contents = infile.readlines()

        for badge in badges:
            if not any(badge in content for content in contents):
                badges_to_add.append(badge)

        if badges_to_add:
            logger.debug(f'updating contents with {badges_to_add}')
            contents.insert(1, ' '.join(badges_to_add))
            contents.insert(2, '\n\n')
    else:
        logger.debug(f'creating new {filename}')
        contents.append(f'# {repo}\n')
        contents.append(' '.join(badges))
        contents.append('\n\n')

    if badges_to_add:
        logger.debug(f'writing {filename}')
        with open(filename, 'w') as outfile:
            outfile.writelines(contents)

    if not exists:
        execute_command('git add README.md', cwd=working_dir, shell=True)


@workflow_step
def commit_change(working_dir):
    """ execute git commit
    """
    execute_command("git commit -am 'docs: Add badges to readme' -s", cwd=working_dir, shell=True)


@workflow_step
def push_branch(working_dir, local_branch):
    """ execute git push
    """
    execute_command(f'git push origin {local_branch}', cwd=working_dir, shell=True)


@workflow_step
def create_pull_request(client, owner_repo, user, default_branch, local_branch, noop=True):
    """ create pull request
    """
    logger.debug(f'creating pull request for {owner_repo}')
    response = client.post(
        f'/repos/{owner_repo}/pulls',
        json={
            'title': 'docs: Add badges to readme',
            'body': 'Add relevant badges to readme',
            'draft': True,
            'base': default_branch,
            'head': f'{user}:{local_branch}'
        },
        noop=noop)
    if noop:
        pull_number = 'noop1213'
    else:
        pull_number = response['number']
    return pull_number


@workflow_step
def verify_pull_request(client, owner_repo, pull_number, noop=True):
    """ verify pull request
    """
    logger.debug(f'verifying {owner_repo} pull request {pull_number}')
    response = client.get(f'/repos/{owner_repo}/pulls/{pull_number}/files', noop=noop)
    if noop:
        return
    if len(response) == 1:
        if response[0]['filename'] == 'README.md':
            logger.debug(f'pull request {pull_number} has been verified')
        else:
            raise PullRequestVerificationFailure(f'{owner_repo} pull request for {pull_number} filename verification failure')
    else:
        raise PullRequestVerificationFailure(f'{owner_repo} pull request for {pull_number} files verification failure')


@workflow_step
def update_pull_request(client, owner_repo, pull_number, reviewers, noop=True):
    """ update pull request with reviewers
    """
    logger.debug(f'updating pull request {owner_repo} {pull_number} with reviewers')
    client.post(
        f'/repos/{owner_repo}/pulls/{pull_number}/requested_reviewers',
        json={
            'reviewers': reviewers
        },
        noop=noop)


@workflow_step
def update_issue(client, owner_repo, pull_number, assignees, labels, milestone_title, noop=True):
    """ update pull request issue with assignees, milestone, and labels
    """
    milestones = client.get(f'/repos/{owner_repo}/milestones', _get='all')
    _, milestone = find(milestones, 'title', milestone_title)
    milestone_number = None
    if milestone:
        milestone_number = milestone['number']
    client.patch(
        f'/repos/{owner_repo}/issues/{pull_number}',
        json={
            'assignees': assignees,
            'milestone': milestone_number,
            'labels': labels
        },
        noop=noop)


def create_pull_request_workflow(data, *args):
    """ create pull rquest workflow for given owner_repo
    """
    owner_repo = data['owner_repo']
    default_branch = data['default_branch']
    local_branch = data['local_branch']
    badges = data['badges']
    reviewers = data['reviewers']
    labels = data['labels']
    milestone = data['milestone']
    noop = data['noop']

    logger.debug(f'creating pull request workflow for {owner_repo} - noop: {noop}')
    logger.debug(f'pull request workflow has a total of {get_workflow_steps()} steps')

    try:
        client, user = get_client()
        check_pull_request(client, owner_repo, user, default_branch, local_branch)
        repo, ssh_url, source_ssh_url = create_fork(client, owner_repo, user)
        working_dir = create_working_dir(repo)
        remove_clone_dir(working_dir, repo)
        clone_repo(working_dir, ssh_url)
        working_dir = f'{working_dir}/{repo}'
        add_remote_upstream(working_dir, source_ssh_url)
        rebase(working_dir, default_branch)
        create_branch(working_dir, local_branch)
        update_readme(badges, repo, working_dir)
        commit_change(working_dir)
        push_branch(working_dir, local_branch)
        pull_number = create_pull_request(client, owner_repo, user, default_branch, local_branch, noop=noop)
        verify_pull_request(client, owner_repo, pull_number, noop=noop)
        update_pull_request(client, owner_repo, pull_number, reviewers, noop=noop)
        update_issue(client, owner_repo, pull_number, [user], labels, milestone, noop=noop)

    except PullRequestExists as exception:
        logger.debug(exception)
        finish_steps()
