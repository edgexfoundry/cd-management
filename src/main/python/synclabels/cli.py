
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

import sys
import json
import logging
from argparse import ArgumentParser
from os import getenv
from datetime import datetime
from synclabels import API

from mpcurses import MPcurses


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
        help='GitHub organization containing repos that serve as the synchronization targets')
    parser.add_argument(
        '--source-repo',
        dest='source_repo',
        type=str,
        default=getenv('GH_SOURCE_REPO'),
        required=False,
        help='GitHub repo containing labels and milestones that serve as the synchronization source')
    parser.add_argument(
        '--exclude-repos',
        dest='exclude_repos',
        type=str,
        default=getenv('GH_EXCLUDE_REPOS'),
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
        help='visualize script execution using a curses screen')
    parser.add_argument(
        '--modified-since',
        dest='modified_since',
        default=None,
        type=str,
        help='choose only sources that have been modified since the duration provided: #[d|h|m] where d=days, h=hours, m=minutes')
    parser.add_argument(
        '--debug',
        dest='debug',
        action='store_true',
        help='display debug messages to stdout')
    parser.add_argument(
        '--execute',
        dest='execute',
        action='store_true',
        help='execute processing - not setting is same as running in NOOP mode')
    return parser


def get_exclude_repos(exclude_repos, source_repo, target_org):
    """ return excluded repos
    """
    excluded_repos = []
    if source_repo.startswith(f'{target_org}/'):
        excluded_repos.append(source_repo.split('/')[1])
    if exclude_repos:
        excluded_repos.extend([exclude_repo.lower().strip() for exclude_repo in exclude_repos.split(',')])
    return excluded_repos


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
        args.modified_since = API.get_gmt_time(args.modified_since)

    # make things simpler with methods below
    args.noop = not args.execute

    if not args.noop:
        dry_run = getenv('DRY_RUN')
        if dry_run and dry_run.lower() == 'true':
            raise ValueError('DRY_RUN true conflicts with --execute being set')


def get_client():
    """ return instance of API
    """
    return API(bearer_token=getenv('GH_TOKEN_PSW'))


def get_screen_layout():
    """ return screen map
    """
    return {
        'default': {
            'window': True,
            'begin_y': 0,
            'begin_x': 0,
            'height': 100,
            'width': 200
        },
        'table': {
            'rows': 20,
            'cols': 3,
            'width': 60,
            'squash': True
        },
        'ratelimit': {
            'position': (3, 59),
            'text': 'RateLimit:',
            'text_color': 245,
            'color': 254,
            'clear': True,
            'regex': r'^INFO: (?P<value>\d+/\d+) resets in .* min$',
        },
        'ratelimit_reset': {
            'position': (4, 59),
            'text': 'Resets In:',
            'text_color': 245,
            'color': 254,
            'clear': True,
            'regex': r'^INFO: \d+/\d+ resets in (?P<value>.*)$',
        },
        'org': {
            'position': (1, 2),
            'text': 'GitHub Org: -',
            'text_color': 245,
            'color': 33,
            'regex': "^'owner' is '(?P<value>.*)'$"
        },
        'source_repo': {
            'position': (2, 2),
            'text': 'Source Repo: -',
            'text_color': 245,
            'color': 33,
            'regex': "^'source_repo' is '(?P<value>.*)'$"
        },
        'source_labels': {
            'position': (3, 5),
            'text': 'Labels: -',
            'text_color': 245,
            'color': 254,
            'regex': "^'labels' has (?P<value>\d+) items$"
        },
        'source_milestones': {
            'position': (3, 18),
            'text': 'Milestones: -',
            'text_color': 245,
            'color': 254,
            'regex': "^'milestones' has (?P<value>\d+) items$"
        },
        'modified_since': {
            'position': (4, 2),
            'text': 'Modified Since: -',
            'text_color': 245,
            'color': 254,
            'regex': "^'modified_since' is '(?P<value>.*)'$"
        },
        'repos': {
            'position': (5, 2),
            'text': 'Repos To Synchronize: 0',
            'text_color': 245,
            'color': 254,
            'regex': '^retrieved total of (?P<value>\d+) repos$'
        },
        'excluded_repos': {
            'position': (6, 2),
            'text': 'Excluded Repos: -',
            'text_color': 245,
            'color': 254,
            'regex': r'^excluded repos: (?P<value>.*)$'
        },
        'noop': {
            'position': (1, 64),
            'text': 'NOOP: -',
            'text_color': 245,
            'color': 239,
            'regex': "^'noop' is '(?P<value>.*)'$"
        },
        'start_time': {
            'position': (6, 61),
            'text': 'Started: -',
            'text_color': 245,
            'color': 254,
            'regex': '^Started:(?P<value>.*)$'
        },
        'end_time': {
            'position': (7, 63),
            'text': 'Ended: -',
            'text_color': 245,
            'color': 254,
            'regex': '^mpcurses: Ended:(?P<value>.*)$'
        },
        'labels_header': {
            'position': (9, 6),
            'text': 'Labels',
            'text_color': 245,
        },
        'milestones_header': {
            'position': (9, 18),
            'text': 'Milestones',
            'text_color': 245,
        },
        'labels_created_header': {
            'position': (10, 4),
            'text': 'CR',
            'text_color': 245,
        },
        'labels_updated_header': {
            'position': (10, 8),
            'text': 'UP',
            'text_color': 245,
        },
        'labels_no_change_header': {
            'position': (10, 12),
            'text': 'NC',
            'text_color': 245,
        },
        'milestones_created_header': {
            'position': (10, 18),
            'text': 'CR',
            'text_color': 245,
        },
        'milestones_updated_header': {
            'position': (10, 22),
            'text': 'UP',
            'text_color': 245,
        },
        'milestones_no_change_header': {
            'position': (10, 26),
            'text': 'NC',
            'text_color': 245,
        },
        '_on': {
            'position': (11, 0),
            'text': '',
            'replace_text': '->',
            'color': 14,
            'regex': r'^INFO: synchronizing \d+ labels to repo .*$',
            'table': True
        },
        '_off': {
            'position': (11, 0),
            'text': '',
            'replace_text': '  ',
            'regex': r'^INFO: synchronization of labels to repo .* is complete$',
            'table': True
        },
        'labels_created': {
            'position': (11, 3),
            'text': '---',
            'text_color': 242,
            'color': 15,
            'keep_count': True,
            'regex': r"^INFO: created label '.*' in repo .*$",
            'zfill': 3,
            'table': True
        },
        'labels_updated': {
            'position': (11, 7),
            'text': '---',
            'text_color': 242,
            'color': 15,
            'keep_count': True,
            'regex': r"^INFO: modified label '.*' in repo .*$",
            'zfill': 3,
            'table': True
        },
        'labels_not_changed': {
            'position': (11, 11),
            'text': '---',
            'text_color': 242,
            'color': 15,
            'keep_count': True,
            'regex': r"^INFO: label '.*' in repo '.*' has not been modified since .*$",
            'zfill': 3,
            'table': True
        },
        'milestones_created': {
            'position': (11, 17),
            'text': '---',
            'text_color': 242,
            'color': 15,
            'keep_count': True,
            'regex': r"^INFO: created milestone in repo .*$",
            'zfill': 3,
            'table': True
        },
        'milestones_updated': {
            'position': (11, 21),
            'text': '---',
            'text_color': 242,
            'color': 15,
            'keep_count': True,
            'regex': r"^INFO: modified milestone '.*' in repo .*$",
            'zfill': 3,
            'table': True
        },
        'milestones_not_changed': {
            'position': (11, 25),
            'text': '---',
            'text_color': 242,
            'color': 15,
            'keep_count': True,
            'regex': r"^INFO: milestone '.*' in repo '.*' has not been modified since .*$",
            'zfill': 3,
            'table': True
        },
        'repo_initialized': {
            'position': (11, 30),
            'text': '',
            'color': 242,
            'width': 30,
            'regex': r"^'repo' is '(?P<value>.*)'$",
            'table': True
        },
        'repo_processing': {
            'position': (11, 30),
            'text': '',
            'color': 14,
            'width': 30,
            'regex': r"^INFO: synchronizing \d+ labels to repo '.*/(?P<value>.*)'$",
            'table': True
        },
        'repo_processed': {
            'position': (11, 30),
            'text': '',
            'color': 15,
            'width': 30,
            'regex': r"^INFO: synchronization of labels to repo '.*/(?P<value>.*)' is complete$",
            'table': True
        },
        'errors': {
            'position': (33, 3),
            'text': 'Errors: -',
            'text_color': 245,
            'color': 237,
            'keep_count': True,
            'regex': r'^ERROR.*$'
        },
        'retries': {
            'position': (34, 2),
            'text': 'Retries: -',
            'text_color': 245,
            'color': 11,
            'keep_count': True,
            'regex': r'^.* - retrying request .*$'
        }
    }


def synchronize(data, shared_data):
    """ synchronize labels and milestones
    """
    client = get_client()
    repo = f"{shared_data['owner']}/{data['repo']}"

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


def initiate_multiprocess(client, args, exclude_repos):
    """ initiate multiprocess execution
    """
    logger.info(f'NOOP: {args.noop}')
    logger.info(f'retrieving matching repos from GitHub {args.target_org}')
    repos = client.get_repos(
        organization=args.target_org,
        # user=args.target_org,  # TESTING ONLY!
        # regex=r'^test_us6379-.*$',  # TESTING ONLY!
        exclude_repos=exclude_repos,
        archived=False,
        disasbled=False)
    logger.info(f"retrieved {len(repos)} repos in '{args.target_org}'")
    if len(repos) == 0:
        logger.info("no repos retrieved - exiting")
        return

    logger.info(f'retrieving labels from {args.source_repo}')
    labels = client.get_labels(args.source_repo)
    logger.info(f"retrieved {len(labels)} labels from label repo '{args.source_repo}'")

    logger.info(f'retrieving milestones from {args.source_repo}')
    milestones = client.get_milestones(args.source_repo)
    logger.info(f'retrieved {len(milestones)} milestones from {args.source_repo}')

    if args.processes > len(repos):
        args.processes = len(repos)

    process_data = [
        {'repo': repo} for repo in repos
    ]
    mpcurses = MPcurses(
        function=synchronize,
        process_data=process_data,
        shared_data={
            'source_repo': args.source_repo,
            'labels': labels,
            'milestones': milestones,
            'owner': args.target_org,
            'modified_since': args.modified_since,
            'noop': args.noop
        },
        processes_to_start=args.processes,
        init_messages=[
            f'retrieved total of {len(repos)} repos',
            f'processing total of {len(repos) * len(labels)} labels',
            f'processing total of {len(repos) * len(milestones)} milestones',
            f'excluded repos: {exclude_repos}',
            f"Started:{datetime.now().strftime('%m/%d/%Y %H:%M:%S')}"
        ],
        screen_layout=get_screen_layout() if args.screen else None)
    mpcurses.execute()

    check_result(process_data)


def set_logging(args):
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)

    logfile = f"{getenv('PWD')}/sync-github-labels.log"
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
        exclude_repos = get_exclude_repos(args.exclude_repos, args.source_repo, args.target_org)
        logger.info(f'excluded repos: {exclude_repos}')

        if not args.processes:
            client.sync_repos(
                args.source_repo,
                organization=args.target_org,
                # user=args.target_org,  # TESTING ONLY!
                # regex=r'^test_us6379-.*$',  # TESTING ONLY!
                exclude_repos=exclude_repos,
                modified_since=args.modified_since,
                noop=args.noop)
        else:
            initiate_multiprocess(client, args, exclude_repos)

    except MissingArgumentError as exception:
        parser.print_usage()
        logger.error(f"ERROR: {str(exception)}")

    except Exception as exception:
        logger.error(f"ERROR: {str(exception)}")
        sys.exit(-1)


if __name__ == '__main__':

    main()
