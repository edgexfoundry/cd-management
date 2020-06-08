
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

from mpcurses import queue_handler
from mpcurses import execute

from githubsync import GitHubAPI
from githubsync.api import get_gmt_time
from argparse import ArgumentParser
from os import getenv
from datetime import datetime
import sys
import json

import logging
logger = logging.getLogger(__name__)


class MissingArgumentError(Exception):
    """ argument error
    """
    pass


def get_parser():
    """ setup parser and return parsed command line arguments
    """
    parser = ArgumentParser(
        description='A Python script to synchronize GitHub labels and milestones')
    parser.add_argument(
        '--target-org',
        dest='target_org',
        type=str,
        default=getenv('GH_TARGET_ORG'),
        required=False,
        help='GitHub organization containing repos that will be the synchronization targets')
    parser.add_argument(
        '--source-repo',
        dest='source_repo',
        type=str,
        default=getenv('GH_SOURCE_REPO'),
        required=False,
        help='GitHub repo that is the source of the labels and milestones')
    parser.add_argument(
        '--blacklist-repos',
        dest='blacklist_repos',
        type=str,
        default=getenv('GH_BLACKLIST_REPOS'),
        required=False,
        help='a comma-delimited list of repos to exclude from synchronization')
    parser.add_argument(
        '--procs',
        dest='processes',
        default=1,
        type=int,
        help='number of concurrent processes to execute')
    parser.add_argument(
        '--screen',
        dest='screen',
        action='store_true',
        help='execute multi-processing dyynamically update curses screen')
    parser.add_argument(
        '--modified-since',
        dest='modified_since',
        default=None,
        type=str,
        help='choose sources that have been modified since the duration provided: #[d|h|m] where d=days, h=hours, m=minutes')
    parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help='enable debug mode')
    parser.add_argument(
        '--noop',
        dest='noop',
        action='store_true',
        help='execute in NOOP mode')
    return parser


def get_blacklist_repos(blacklist_repos):
    """ return blacklist repos
    """
    if blacklist_repos:
        return [blacklist_repo.lower().strip() for blacklist_repo in blacklist_repos.split(',')]


def validate(args):
    """ validate args
    """
    if not args.target_org:
        raise MissingArgumentError(
            'the following arguments are required: --target-org or GH_TARGET_ORG must be set in environment')

    if not args.source_repo:
        raise MissingArgumentError(
            'the following arguments are required: --source-repo or GH_SOURCE_REPO must be set in environment')

    if args.modified_since:
        args.modified_since = get_gmt_time(args.modified_since)

    if not args.noop:
        dry_run = getenv('DRY_RUN')
        if dry_run and dry_run.lower() == 'true':
            args.noop = True


def get_client():
    """ return instance of GitHubAPI
    """
    return GitHubAPI.get_client()


def get_screen_layout():
    """ return screen map
    """
    return {
        'target_org': {
            'text': 'Target GitHub Org: -',
            'text_color': 245,
            'color': 27,
            'position': (1, 0),
            'regex': "^'owner' is '(?P<value>.*)'$"
        },
        'noop': {
            'text': 'NOOP: -',
            'text_color': 245,
            'color': 254,
            'position': (1, 59),
            'regex': "^'noop' is '(?P<value>.*)'$"
        },
        'modified_since': {
            'text': 'Modified Since: -',
            'text_color': 245,
            'color': 254,
            'position': (2, 49),
            'regex': "^'modified_since' is '(?P<value>.*)'$"
        },
        'source_repo': {
            'text': 'Source Repo: -',
            'text_color': 245,
            'color': 27,
            'position': (2, 0),
            'regex': "^'source_repo' is '(?P<value>.*)'$"
        },
        'repos': {
            'text': 'Repos: 0',
            'text_color': 245,
            'color': 254,
            'position': (3, 0),
            'regex': '^retrieved total of (?P<value>\d+) repos$'
        },
        'ratelimit': {
            'text': 'RateLimit:',
            'text_color': 245,
            'color': 254,
            'position': (4, 54),
            'clear': True,
            'regex': '^(?P<value>\d+/\d+) resets in .* min$'
        },
        'total_labels': {
            'text': 'Labels: 0',
            'text_color': 245,
            'color': 0,
            'position': (4, 14),
            'regex': "^'labels' has (?P<value>\d+) items$"
        },
        'total_milestones': {
            'text': 'Milestones: 0',
            'text_color': 245,
            'color': 0,
            'position': (4, 27),
            'regex': "^'milestones' has (?P<value>\d+) items$"
        },
        'ratelimit_reset': {
            'text': 'Resets In:',
            'text_color': 245,
            'color': 254,
            'position': (5, 54),
            'clear': True,
            'regex': '^\d+/\d+ resets in (?P<value>.*)$'
        },
        'to_process': {
            'text': 'To Process -',
            'text_color': 245,
            'position': (5, 1)
        },
        'to_process_labels': {
            'text': 'Labels: 0',
            'text_color': 245,
            'color': 0,
            'position': (5, 14),
            'regex': '^processing total of (?P<value>\d+) labels$'
        },
        'to_process_milestones': {
            'text': 'Milestones: 0',
            'text_color': 245,
            'color': 0,
            'position': (5, 27),
            'regex': '^processing total of (?P<value>\d+) milestones$'
        },
        'created': {
            'text': 'Created -',
            'text_color': 245,
            'position': (6, 4)
        },
        'created_labels': {
            'text': 'Labels: 0',
            'text_color': 245,
            'color': 235,
            'position': (6, 14),
            'keep_count': True,
            'zfill': 4,
            'regex': '^.*created label.*$'
        },
        'created_milestones': {
            'text': 'Milestones: 0',
            'text_color': 245,
            'color': 235,
            'position': (6, 27),
            'keep_count': True,
            'zfill': 4,
            'regex': '^.*created milestone.*$'
        },
        'modified': {
            'text': 'Modified -',
            'text_color': 245,
            'position': (7, 3)
        },
        'modified_labels': {
            'text': 'Labels: 0',
            'text_color': 245,
            'color': 239,
            'position': (7, 14),
            'keep_count': True,
            'zfill': 4,
            'regex': '^.*modified label.*$'
        },
        'modified_milestones': {
            'text': 'Milestones: 0',
            'text_color': 245,
            'color': 239,
            'position': (7, 27),
            'keep_count': True,
            'zfill': 4,
            'regex': '^.*modified milestone.*$'
        },
        'no_change': {
            'text': 'No Change -',
            'text_color': 245,
            'color': 0,
            'position': (8, 2)
        },
        'not_modified_labels': {
            'text': 'Labels: 0',
            'text_color': 245,
            'color': 236,
            'position': (8, 14),
            'keep_count': True,
            'zfill': 4,
            'regex': '^.*label .* has not been modified since.*$'
        },
        'not_modified_milestones': {
            'text': 'Milestones: 0',
            'text_color': 245,
            'color': 236,
            'position': (8, 27),
            'keep_count': True,
            'zfill': 4,
            'regex': '^.*milestone .* has not been modified since.*$'
        },
        'errors': {
            'text': 'Errors: 0',
            'text_color': 245,
            'color': 237,
            'position': (9, 0),
            'keep_count': True,
            'regex': '^ERROR.*$'
        },
        'retries': {
            'text': 'Retries: 0',
            'text_color': 245,
            'color': 232,
            'position': (9, 12),
            'keep_count': True,
            'regex': '^.* - retrying request in .*$'
        },
        'status_indicator': {
            'text': '',
            'replace_text': '>',
            'color': 14,
            'position': (11, 0),
            'regex': '^INFO: synchronizing.*$'
        },
        'status': {
            'text': '',
            'color': 14,
            'position': (11, 2),
            'clear': True,
            'regex': '^INFO: (?P<value>.*)$'
        },
        'processes': {
            'text': 'Processes -',
            'text_color': 245,
            'position': (12, 2)
        },
        'procs_active': {
            'text': 'Active: 0',
            'text_color': 245,
            'color': 6,
            'position': (12, 14),
            'regex': '^mpcurses: number of active processes (?P<value>\d+)$'
        },
        'procs_queued': {
            'text': 'Queued: 0',
            'text_color': 245,
            'color': 6,
            'position': (12, 26),
            'regex': '^mpcurses: number of queued processes (?P<value>\d+)$'
        },
        'procs_complete': {
            'text': 'Completed: 0',
            'text_color': 245,
            'color': 6,
            'position': (12, 38),
            'keep_count': True,
            'regex': '^mpcurses: a process has completed$'
        },
        'start_time': {
            'text': 'Started: -',
            'text_color': 245,
            'color': 159,
            'position': (7, 56),
            'regex': '^Started:(?P<value>.*)$'
        },
        'end_time': {
            'text': 'Ended: -',
            'text_color': 245,
            'color': 159,
            'position': (8, 58),
            'regex': '^mpcurses: Ended:(?P<value>.*)$'
        }
    }


@queue_handler
def synchronize(data, shared_data):
    client = shared_data['client']
    repo = '{}/{}'.format(shared_data['owner'], data['repo'])

    client.sync_labels(
        repo,
        shared_data['labels'],
        shared_data['source_repo'],
        modified_since=shared_data['modified_since'],
        noop=shared_data['noop'])

    client.sync_milestones(
        repo,
        shared_data['milestones'],
        shared_data['source_repo'],
        modified_since=shared_data['modified_since'],
        noop=shared_data['noop'])


def check_result(process_data):
    """ raise exception if any result in process data is exception
    """
    if any([isinstance(process.get('result'), Exception) for process in process_data]):
        raise Exception('one or more processes had errors')


def initiate_multiprocess(client, args, blacklist_repos):
    """ initiate multiprocess execution
    """
    logger.info('NOOP: {}'.format(args.noop))
    logger.info('retrieving matching repos from GitHub {}'.format(args.target_org))
    repos = client.get_repos(
        organization=args.target_org,
        # user=args.target_org,  # TESTING ONLY!
        # regex=r'^test_us6379-.*$',  # TESTING ONLY!
        blacklist_repos=blacklist_repos,
        archived=False,
        disasbled=False)
    logger.info("retrieved {} repos in '{}'".format(len(repos), args.target_org))
    if len(repos) == 0:
        logger.info("no repos retrieved - exiting")
        return

    logger.info('retrieving labels from {}'.format(args.source_repo))
    labels = client.get_labels(args.source_repo)
    logger.info("retrieved {} labels from label repo '{}'".format(len(labels), args.source_repo))

    logger.info('retrieving milestones from {}'.format(args.source_repo))
    milestones = client.get_milestones(args.source_repo)
    logger.info('retrieved {} milestones from {}'.format(len(milestones), args.source_repo))

    if args.processes > len(repos):
        args.processes = len(repos)

    process_data = [
        {'repo': repo} for repo in repos
    ]
    execute(
        function=synchronize,
        process_data=process_data,
        shared_data={
            'client': client,
            'source_repo': args.source_repo,
            'labels': labels,
            'milestones': milestones,
            'owner': args.target_org,
            'modified_since': args.modified_since,
            'noop': args.noop
        },
        number_of_processes=args.processes,
        init_messages=[
            'retrieved total of {} repos'.format(len(repos)),
            'processing total of {} labels'.format(len(repos) * len(labels)),
            'processing total of {} milestones'.format(len(repos) * len(milestones)),
            'Started:{}'.format(datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
        ],
        screen_layout=get_screen_layout() if args.screen else None)

    check_result(process_data)


def set_logging(args):
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)

    logfile = '{}/githubsync.log'.format(getenv('PWD'))
    file_handler = logging.FileHandler(logfile)
    file_formatter = logging.Formatter("%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    rootLogger.addHandler(file_handler)

    if not args.screen:
        stream_handler = logging.StreamHandler()
        stream_formatter = logging.Formatter('%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s')
        stream_handler.setFormatter(stream_formatter)
        stream_handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
        rootLogger.addHandler(stream_handler)


def main():
    """ main function
    """
    parser = get_parser()
    try:
        args = parser.parse_args()
        validate(args)
        set_logging(args)
        client = get_client()
        blacklist_repos = get_blacklist_repos(args.blacklist_repos)
        logger.info('black listed repos: {}'.format(blacklist_repos))

        if not args.processes:
            client.sync_repos(
                args.source_repo,
                organization=args.target_org,
                # user=args.target_org,  # TESTING ONLY!
                # regex=r'^test_us6379-.*$',  # TESTING ONLY!
                blacklist_repos=blacklist_repos,
                modified_since=args.modified_since,
                noop=args.noop)
        else:
            initiate_multiprocess(client, args, blacklist_repos)

    except MissingArgumentError as exception:
        parser.print_usage()
        logger.error("ERROR: {}".format(str(exception)))

    except Exception as exception:
        logger.error("ERROR: {}".format(str(exception)))
        sys.exit(-1)


if __name__ == '__main__':

    main()
