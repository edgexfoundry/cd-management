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

from rest3client import RESTclient
from argparse import ArgumentParser
from os import getenv
from datetime import datetime, timezone

import sys
import csv

from mpcurses import MPcurses

import dateutil.parser
import pytz
import logging


logger = logging.getLogger(__name__)

logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').propagate = False


class MissingArgumentError(Exception):
    """ argument error
    """
    pass


def get_parser():
    """ setup parser and return parsed command line arguments
    """
    parser = ArgumentParser(
        description="""A Python script scrapes the hub.docker.com REST API to
    determine which images are "stale" from the edgexfoundry organization.""")
    parser.add_argument(
        '--docker-user',
        dest='docker_user',
        type=str,
        default='edgexfoundry',
        required=False,
        help='Docker User')
    parser.add_argument(
        '--dockerhub-host-api',
        dest='dockerhub_host_api',
        type=str,
        default='hub.docker.com/v2',
        required=False,
        help='hub.docker.com host API')
    parser.add_argument(
        '--csv',
        dest='csv',
        action='store_true',
        help='write jobs to CSV file')
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
    return parser


def validate(args):
    """ validate args
    """
    if args.screen:
        if args.processes == 1:
            args.processes = 10


def get_dockerhub_client(dockerhub_host_api):
    """ return instance of RESTclient for hub.docker.com
    """
    logger.info('connecting to hub.docker.com: {}'.format(dockerhub_host_api))

    return RESTclient(dockerhub_host_api)


def get_screen_layout():
    """ return screen map
    """
    return {
        'start_time': {
            'position': (1, 3),
            'text': 'Started: -',
            'text_color': 245,
            'color': 254,
            'regex': '^Started:(?P<value>.*)$'
        },
        'end_time': {
            'position': (2, 5),
            'text': 'Ended: -',
            'text_color': 245,
            'color': 254,
            'regex': '^mpcurses: Ended:(?P<value>.*)$'
        },
        'images_processed': {
            'position': (5, 1),
            'text': 'Docker Images Processed: 0',
            'text_color': 245,
            'color': 2,
            'keep_count': True,
            'regex': '^Fetching information about:.*$'
        },
        'images_tot': {
            'position': (4, 5),
            'text': 'Docker Images Total: -',
            'text_color': 245,
            'color': 2,
            'regex': '^Total Image Count:(?P<value>\\d+).*$'
        },
        'processed_tags': {
            'position': (7, 10),
            'text': 'Tags Processed: 0',
            'text_color': 245,
            'color': 2,
            'keep_count': True,
            'regex': '^Tag Processed.*$'
        }
    }


def configure_logging(args):
    """ configure logging
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    name = 'dockerhub-audit.log'

    logfile = '{}/{}'.format(getenv('PWD'), name)
    file_handler = logging.FileHandler(logfile)
    file_formatter = logging.Formatter("%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    if not args.screen:
        stream_handler = logging.StreamHandler()
        formatter = '%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s'
        if not args.processes:
            formatter = '%(asctime)s %(name)s [%(funcName)s] %(levelname)s %(message)s'
        stream_formatter = logging.Formatter(formatter)
        stream_handler.setFormatter(stream_formatter)
        stream_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(stream_handler)


def write_csv(*, name, images, headerStart=[]):
    """ write jobs to csv file
    """
    now = datetime.utcnow()
    filename = '{}-{}-{}.csv'.format("dockerhub",
                                     name,
                                     now.strftime('%m.%d.%Y-%H.%M.%S'))
    logger.debug('writing {}'.format(filename))
    headers = list(images[0].keys())

    if headerStart is not None:
        for headerItem in headerStart:
            headers.pop(headers.index(headerItem))
        headers = headerStart + headers

    with open(filename, 'w') as output:
        writer = csv.DictWriter(output, headers)
        writer.writeheader()
        writer.writerows(images)
    logger.info('created file: {}'.format(filename))


def get_image_count(args, client):
    response = client.get('/repositories/{}'.format(args.docker_user))
    logger.debug('Total Image Count:{}'.format(response['count']))
    return response['count']


def get_all_images(args, client):
    response = client.get('/repositories/{}?page_size=1000'.
                          format(args.docker_user))
    return response['results']


def filter_image_list(image_dict_list):
    for image in image_dict_list:
        image.pop("repository_type", None)
        image.pop("status", None)
        image.pop("description", None)
        image.pop("is_private", None)
        image.pop("is_automated", None)
        image.pop("can_edit", None)
        image.pop("is_migrated", None)
        image.pop("namespace", None)
        image['pull_count'] = int(image['pull_count'])
    return image_dict_list


def filter_tag_list(tag_dict_list):
    # Scrape out the results from the the MP work:
    just_tags_list = []
    for item in tag_dict_list:
        result = item.get('result')
        if not result:
            raise ValueError(f"repository {item['name']} is missing result")
        just_tags_list.extend(item['result'])

    return just_tags_list


def check_result(process_data):
    """ raise exception if any result in process data is exception
    """
    if any([isinstance(process.get('result'), Exception) for process in process_data]):
        raise Exception('one or more processes had errors')


def get_all_tags(function, args, image_dict_list):
    screen_layout = None
    if args.screen:
        screen_layout = get_screen_layout()

    shared_data = {
        'args': args,
    }
    if args.processes > 1:
        MPcurses(
            function=function,
            process_data=image_dict_list,
            shared_data=shared_data,
            processes_to_start=args.processes,
            init_messages=[
                f"Total Image Count:{len(image_dict_list)}",
                f"Started:{datetime.now().strftime('%m/%d/%Y %H:%M:%S')}"
            ],
            screen_layout=screen_layout).execute()
        check_result(image_dict_list)
    else:
        for i, image in enumerate(image_dict_list):
            image_dict_list[i]['result'] = get_tags(image, shared_data)

    return image_dict_list


def get_tags(image, shared_data):
    utc = pytz.UTC
    args = shared_data['args']
    client = get_dockerhub_client(args.dockerhub_host_api)
    image_tags_dict_list = []
    logger.debug('Fetching information about: {}'.format(image['name']))
    response = client.get('/repositories/{}/{}/tags/?page_size=1000'.
                          format(args.docker_user, image['name']))
    for tag in response['results']:
        tag['repo_name'] = image['name']
        tag['repo_star_count'] = image['star_count']
        tag['repo_pull_count'] = image['pull_count']
        tag.pop("last_updater", None)
        tag.pop("v2", None)
        tag.pop("id", None)
        tag.pop("creator", None)
        tag.pop("image_id", None)
        tag.pop("repository", None)
        tag['architecture'] = tag['images'][0]['architecture']
        tag['os'] = tag['images'][0]['os']
        tag.pop("images", None)
        tag['tag_name'] = tag['name']
        tag.pop('name', None)
        tag['size_in_MB'] = round(tag['full_size'] / 1024 / 1024, 2)
        tag.pop('full_size', None)
        tag['days_since_update'] = (utc.localize(datetime.utcnow()) - dateutil.parser.isoparse(tag['last_updated'])).days
        image_tags_dict_list.append(tag)

        logger.debug(f"Tag Processed {image['name']}:{tag['tag_name']}")
    return image_tags_dict_list


def main():
    """ main function
    """
    parser = get_parser()
    try:
        args = parser.parse_args()
        validate(args)

        configure_logging(args)

        dockerhub_client = get_dockerhub_client(args.dockerhub_host_api)

        image_dict_list = get_all_images(args, dockerhub_client)
        image_dict_list = filter_image_list(image_dict_list)

        # this takes a while
        image_tags_dict_list = get_all_tags(
            get_tags,
            args,
            image_dict_list)

        image_tags_dict_list = filter_tag_list(image_tags_dict_list)

        if args.csv:
            write_csv(name="tags", images=image_tags_dict_list,
                      headerStart=['repo_name',
                                   'tag_name',
                                   'architecture',
                                   'os',
                                   'size_in_MB',
                                   'repo_star_count',
                                   'repo_pull_count',
                                   'last_updater_username',
                                   'last_updated',
                                   'days_since_update'
                                   ])
    except MissingArgumentError as exception:
        parser.print_usage()
        logger.error("ERROR: {}".format(str(exception)))


if __name__ == '__main__':  # pragma: no cover

    main()
