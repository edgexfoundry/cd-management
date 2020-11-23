
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
from os import getenv
from datetime import datetime
from argparse import ArgumentParser

from semantic_version import SimpleSpec
from mpcurses import MPcurses
from prunetags import API


logger = logging.getLogger(__name__)


class MissingArgumentError(Exception):
    """ argument error
    """
    pass


def get_parser():
    """ setup parser and return parsed command line arguments
    """
    parser = ArgumentParser(
        description='A Python script that removes old prerelease tags from repos in a GitHub org')
    parser.add_argument(
        '--org',
        dest='org',
        type=str,
        default=getenv('GH_ORG'),
        required=False,
        help='GitHub organization containing repos to process')
    parser.add_argument(
        '--user',
        dest='user',
        type=str,
        default=getenv('GH_USER'),
        required=False,
        help='GitHub user containing repos to process')
    parser.add_argument(
        '--exclude-repos',
        dest='exclude_repos',
        type=str,
        default=getenv('GH_EXCLUDE_REPOS'),
        required=False,
        help='a regex to match name of repos to exclude from processing')
    parser.add_argument(
        '--include-repos',
        dest='include_repos',
        type=str,
        default=None,
        required=False,
        help='a regex to match name of repos to include in processing')
    parser.add_argument(
        '--report',
        dest='report',
        action='store_true',
        help='generate and save report but do not process')
    parser.add_argument(
        '--procs',
        dest='processes',
        default=0,
        type=int,
        help='number of concurrent processes to execute')
    parser.add_argument(
        '--screen',
        dest='screen',
        action='store_true',
        help='visualize script execution using a curses screen')
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
    parser.add_argument(
        '--remove-version',
        dest='version',
        type=str,
        default=None,
        required=False,
        help='version expression to remove- e.g. \'<1.0.50\', \'>1.0.87\', \'<1.1.4,>=1.0.1\'')
    return parser


def validate(args):
    """ validate args
    """
    if not args.org and not args.user:
        raise MissingArgumentError(
            'the following arguments are required: --org or GH_ORG must be set in environment')

    if args.org and args.user:
        raise MissingArgumentError(
            'cannot set --org and --user simultaneously')

    # make things simpler with methods below
    args.noop = not args.execute

    if not args.noop:
        dry_run = getenv('DRY_RUN')
        if dry_run and dry_run.lower() == 'true':
            raise ValueError('DRY_RUN true conflicts with --execute being set')

    if args.screen:
        if not args.processes:
            args.processes = 10

    if args.version:
        try:
            SimpleSpec(args.version)
        except Exception:
            raise ValueError('Invalid version arguement syntax. See README for reference')


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
            'width': 55,
            'squash': True
        },
        'ratelimit': {
            'position': (3, 59),
            'text': 'RateLimit:',
            'text_color': 245,
            'color': 254,
            'regex': r'^INFO: (?P<value>\d+/\d+) resets in .* min$',
        },
        'ratelimit_reset': {
            'position': (4, 59),
            'text': 'Resets In:',
            'text_color': 245,
            'color': 254,
            'regex': r'^INFO: \d+/\d+ resets in (?P<value>.*)$',
        },
        'org': {
            'position': (1, 2),
            'text': 'GitHub Org: -',
            'text_color': 245,
            'color': 33,
            'regex': "^'owner' is '(?P<value>.*)'$"
        },
        'include_repos': {
            'position': (2, 2),
            'text': 'Include-Repos: -',
            'text_color': 245,
            'color': 254,
            'width': 48,
            'regex': "^'include_repos' is '(?P<value>.*)'$"
        },
        'exclude_repos': {
            'position': (3, 2),
            'text': 'Exclude-Repos: -',
            'text_color': 245,
            'color': 254,
            'width': 48,
            'regex': "^'exclude_repos' is '(?P<value>.*)'$"
        },
        'repos': {
            'position': (4, 2),
            'text': 'Repos: 0',
            'text_color': 245,
            'color': 254,
            'regex': '^retrieved total of (?P<value>\d+) repos$'
        },
        'noop': {
            'position': (1, 64),
            'text': 'NOOP: -',
            'text_color': 245,
            'color': 239,
            'regex': "^'noop' is '(?P<value>.*)'$"
        },
        'version_opt': {
            'position': (2, 52),
            'text': 'Version Argument: -',
            'text_color': 245,
            'color': 239,
            'regex': "^'version' is '(?P<value>.*)'$"
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
        'tpt_key1': {
            'position': (6, 2),
            'text': 'TPT:',
            'text_color': 245,
        },
        'tpt_key2': {
            'position': (6, 7),
            'text': 'Total Pre-release Tags',
            'text_color': 254,
        },
        'ptr_key1': {
            'position': (7, 2),
            'text': 'PTR:',
            'text_color': 245,
        },
        'ptr_key2': {
            'position': (7, 7),
            'text': 'Pre-release Tags Removed',
            'text_color': 254,
        },
        'tpt_header': {
            'position': (9, 2),
            'text': 'TPT',
            'text_color': 245,
        },
        'ptr_header': {
            'position': (9, 6),
            'text': 'PTR',
            'text_color': 245,
        },
        'version_header': {
            'position': (9, 16),
            'text': 'Version',
            'text_color': 245,
        },
        'repo_header': {
            'position': (9, 25),
            'text': 'Repo',
            'text_color': 245,
        },
        '_on': {
            'position': (10, 0),
            'text': '',
            'replace_text': '->',
            'color': 14,
            'regex': r'^INFO: removing (prerelease|version) tags from repo .*/(?P<value>.*)$',
            'table': True
        },
        '_off': {
            'position': (10, 0),
            'text': '',
            'replace_text': '  ',
            'regex': r'^processed repo .*$',
            'table': True
        },
        'tags': {
            'position': (10, 2),
            'text': '---',
            'text_color': 242,
            'color': 15,
            'regex': r'^repo .* has (?P<value>.*) (prerelease|version) tags that can be removed.*$',
            'table': True,
        },
        'tags_removed': {
            'position': (10, 6),
            'text': '---',
            'text_color': 242,
            'color': 15,
            'keep_count': True,
            'regex': r'^INFO: removed tag .* from repo .*$',
            'zfill': 3,
            'table': True
        },
        'version': {
            'position': (10, 10),
            'text': '--------------',
            'text_color': 242,
            'color': 15,
            'width': 14,
            'right_justify': True,
            'regex': r'^repo .* latest tag version is (?P<value>.*)$',
            'table': True
        },
        'repo_initialized': {
            'position': (10, 25),
            'text': '',
            'color': 242,
            'width': 30,
            'regex': r"^'repo' is '.*/(?P<value>.*)'$",
            'table': True
        },
        'repo_processing': {
            'position': (10, 25),
            'text': '',
            'color': 14,
            'width': 30,
            'regex': r'^INFO: removing (prerelease|version) tags from repo .*/(?P<value>.*)$',
            'table': True
        },
        'repo_processed': {
            'position': (10, 25),
            'text': '',
            'color': 15,
            'width': 30,
            'regex': r'^removed (prerelease|version) tags from repo .*/(?P<value>.*)$',
            'table': True
        },
        'repo_no_tags': {
            'position': (10, 25),
            'text': '',
            # 'color': 242,
            'color': 3,
            'width': 30,
            'regex': r'^INFO: repo .*/(?P<value>.*) has no tags.*$',
            'table': True
        },
        'processes': {
            'position': (32, 2),
            'text': 'Processes:',
            'text_color': 245,
        },
        'processes_active': {
            'position': (33, 5),
            'text': 'Active: 0',
            'text_color': 245,
            'color': 14,
            'regex': r'^mpcurses: number of active processes (?P<value>\d+)$',
            'effects': [
                {
                    'regex': r'^mpcurses: number of active processes 000$',
                    'color': 7
                }
            ],
        },
        'processes_queued': {
            'position': (34, 5),
            'text': 'Queued: 0',
            'text_color': 245,
            'color': 254,
            'regex': r'^mpcurses: number of queued processes (?P<value>\d+)$',
            'effects': [
                {
                    'regex': r'^mpcurses: number of queued processes 000$',
                    'color': 7
                }
            ],
        },
        'processes_complete': {
            'position': (35, 2),
            'text': 'Completed: -',
            'text_color': 245,
            'color': 254,
            'keep_count': True,
            'regex': r'^mpcurses: a process has completed$'
        },
        'errors': {
            'position': (33, 28),
            'text': 'Errors: -',
            'text_color': 245,
            'color': 237,
            'keep_count': True,
            'regex': r'^ERROR.*$'
        },
        'retries': {
            'position': (34, 27),
            'text': 'Retries: -',
            'text_color': 245,
            'color': 11,
            'keep_count': True,
            'regex': r'^.* - retrying request in .*$'
        },
    }


def version_screen_layout(screen_layout):
    screen_layout['tpt_key1']['text'] = 'TT:'
    screen_layout['tpt_key2']['text'] = 'Total Tags'
    screen_layout['ptr_key1']['text'] = 'TR:'
    screen_layout['ptr_key2']['text'] = 'Tags Removed'
    screen_layout['tpt_header']['text'] = 'TT'
    screen_layout['ptr_header']['text'] = 'TR'
    return screen_layout


def remove_prerelease_tags(data, shared_data):
    repo = data['repo']
    client = shared_data['client']
    noop = shared_data['noop']
    client.remove_prerelease_tags(repo=repo, noop=noop)
    logger.debug(f'processed repo {repo}')


def get_prerelease_tags_report(data, shared_data):
    repo = data['repo']
    client = shared_data['client']
    report = client.get_prerelease_tags_report(repos=[repo])
    return report


def remove_version_tags(data, shared_data):
    repo = data['repo']
    client = shared_data['client']
    noop = shared_data['noop']
    expression = shared_data['version']
    client.remove_version_tags(repo=repo, noop=noop, expression=expression)
    logger.debug(f'processed repo {repo}')


def get_version_tags_report(data, shared_data):
    repo = data['repo']
    client = shared_data['client']
    expression = shared_data['version']
    report = client.get_version_tags_report(repos=[repo], expression=expression)
    return report


def check_result(process_data):
    """ raise exception if any result in process data is exception
    """
    if any([isinstance(process.get('result'), Exception) for process in process_data]):
        raise Exception('one or more processes had errors')


def initiate_multiprocess(client, function, args, owner, repos):
    """ initiate multiprocess execution
    """
    if args.processes == 0 or args.processes > len(repos):
        args.processes = len(repos)

    process_data = [
        {'repo': repo} for repo in repos
    ]

    screen_layout = None
    if args.screen:
        screen_layout = get_screen_layout()
        if args.version:
            screen_layout = version_screen_layout(screen_layout)

    include_repos = args.include_repos if args.include_repos else '-'
    exclude_repos = args.exclude_repos if args.exclude_repos else '-'

    # this is where magic happens
    # the MPcurses class takes care of starting the required number of processes
    # and handles all the managing all processes and message queues - you just tell it
    # what function to execute within each process, the data each process needs to execute,
    # the total number of processes to execute and the screen layout (if any)
    mpcurses = MPcurses(
        function=function,
        process_data=process_data,
        shared_data={
            'client': client,
            'owner': owner,
            'noop': args.noop,
            'version': args.version
        },
        processes_to_start=args.processes,
        init_messages=[
            f"'include_repos' is '{include_repos}'",
            f"'exclude_repos' is '{exclude_repos}'",
            f'retrieved total of {len(repos)} repos',
            f"Started:{datetime.now().strftime('%m/%d/%Y %H:%M:%S')}"
        ],
        screen_layout=screen_layout)
    mpcurses.execute()

    check_result(process_data)
    return process_data


def set_logging(args):
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)

    logfile = '{}/prune-github-tags.log'.format(getenv('PWD'))
    file_handler = logging.FileHandler(logfile)
    file_formatter = logging.Formatter("%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    rootLogger.addHandler(file_handler)

    if not args.screen and not args.report:
        stream_handler = logging.StreamHandler()
        formatter = '%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s'
        if not args.processes:
            formatter = '%(asctime)s %(name)s [%(funcName)s] %(levelname)s %(message)s'
        stream_formatter = logging.Formatter(formatter)
        stream_handler.setFormatter(stream_formatter)
        stream_handler.setLevel(logging.DEBUG if args.debug else logging.INFO)
        rootLogger.addHandler(stream_handler)


def get_repos(client, args):
    """ return matching repos
    """
    logger.info(f'NOOP: {args.noop}')

    owner = args.org
    if args.user:
        owner = args.user

    message = f'retrieving matching repos from org/user {owner}'
    logger.info(message)
    if args.screen or args.report:
        print(f'{message} ...')

    repos = client.get_repos(
        organization=args.org,
        user=args.user,
        include=args.include_repos,
        exclude=args.exclude_repos,
        archived=False,
        disabled=False)

    logger.info(f"retrieved {len(repos)} repos from org/owner '{owner}'")
    return owner, repos


def prune_prerelease_tags(client, repos, args):
    """ prune prerelease tags from all repos
    """
    for repo in repos:
        client.remove_prerelease_tags(repo=repo, noop=args.noop)


def prune_version_tags(client, repos, args):
    """ prune version tags from all repos
    """
    for repo in repos:
        client.remove_version_tags(repo=repo, noop=args.noop, expression=args.version)


def write_json_file(report, owner):
    """ write json file
    """
    now = datetime.utcnow()
    filename = f"{owner}-{now.strftime('%m.%d.%Y-%H.%M.%S')}.json"
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(report, json_file, ensure_ascii=False, indent=4)
    print(f'saved report to: {filename}')


def write_report(result, owner):
    """ write report
    """
    report = {}
    for item in result:
        report.update(item['result'])
    if len(result) == 1:
        print(json.dumps(report, indent=4))
    write_json_file(report, owner)


def main():
    """ main function
    """
    parser = get_parser()
    try:
        args = parser.parse_args()
        validate(args)
        set_logging(args)
        client = get_client()
        owner, repos = get_repos(client, args)
        if not repos:
            logger.info("no repos retrieved - exiting")
            return
        if not args.report and not args.processes:
            # boring sequential execution - it does the job but its kinda boring
            if not args.version:
                prune_prerelease_tags(client, repos, args)
            else:
                prune_version_tags(client, repos, args)
        else:
            # exciting multi-process execution leveraging the mpcurses library
            # note the same api methods are called here as in the call above
            # the only special thing we have to do is wrap the api calls with
            # an mpcurses method and create a dictionary describing the curses
            # screen layout

            # also note the api methods (API) know nothing about how they are being called
            # whether it is being called within the context of a single process or
            # scaled across multiple processes - they also know nothing about the curses screen
            # the mpcurses library abstracts multi-processing and the curses screen completely
            # from the api methods - that's the way it should be
            if args.report:
                if not args.version:
                    result = initiate_multiprocess(client, get_prerelease_tags_report, args, owner, repos)
                else:
                    result = initiate_multiprocess(client, get_version_tags_report, args, owner, repos)
                write_report(result, owner)
            else:
                if not args.version:
                    initiate_multiprocess(client, remove_prerelease_tags, args, owner, repos)
                else:
                    initiate_multiprocess(client, remove_version_tags, args, owner, repos)

    except MissingArgumentError as exception:
        parser.print_usage()
        logger.error("ERROR: {}".format(str(exception)))

    except Exception as exception:
        logger.error("ERROR: {}".format(str(exception)))
        sys.exit(-1)


if __name__ == '__main__':  # pragma: no cover

    main()
