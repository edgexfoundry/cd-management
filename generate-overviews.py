#!/usr/bin/python3
# /*******************************************************************************
#  Copyright 2021 IOTech Systems LTD
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
#  in compliance with the License. You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License
#  is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing permissions and limitations under
#  the License.
# *******************************************************************************/

import os
import sys
import requests
from argparse import ArgumentParser

MARKER = "$$"
LIST_IMAGES = 'https://hub.docker.com/v2/repositories/%(org)s/'


def get_args():
    """ setup parser and return parsed command line arguments
    """
    parser = ArgumentParser(
        description='A Python script that generate DockerHub overview as Markdown files')
    parser.add_argument(
        '--template-base',
        type=str,
        default='new-names',
        required=False,
        help='which directory under image-overview-templates to use. Possible values [legacy-names, new-names]')
    parser.add_argument(
        '--org',
        type=str,
        default='edgexfoundry',
        required=False,
        help='DockerHub org containing the Docker images')
    parser.add_argument(
        '--offline',
        action='store_true',
        help='generate overviews from local templates')
    return parser.parse_args()

def get_file_content(filename):
    content = ""
    # if the content file can be opened, return the content in the file; otherwise specify missing content in markdown
    try:
        f = open(filename, "r")
        content = f.read()
        f.close()
    except FileNotFoundError:
        print("\tNo content file %s" % filename)
        content = "**no content file**\n"
    except:
        print("\tTrouble opening file %s" % filename)
        content = "**missing content**\n"
    return content

def replace_line_with_content(input_line):
    # get the input line minus the marker to get the content file
    content_file_name = input_line[len(MARKER):-1]
    # return the content from the content file
    return get_file_content(content_file_name)

def add_content(input_line, output):
    # if the line of content is markered - then get the replacement content specified by the file
    if input_line.startswith(MARKER):
        input_line = replace_line_with_content(input_line)
    # return the line or the replacement content
    output.write(input_line)

def create_overview(image_name, template_base='new-names'):
    try:
        # open the template file for the image
        template = open(f"./image-overview-templates/{template_base}/{image_name}.md", "r")
    except FileNotFoundError:
        print("No template file %s" % image_name)
        return
    except:
        print("Trouble opening template file %s" % image_name)
        return
    try:
        # open the output overview file for the image
        output = open(f"./generated-overviews/{template_base}/{image_name}.md", "w")
    except:
        print("Cannot open overview file for: %s" % image_name)
        return
    # for each line in the template, write out the appropriate line of content in the output file
    for template_line in template:
        add_content(template_line, output)
    output.close()
    template.close()
    print("Overview created for %s" % image_name)

def process_online(args):
    next_page = LIST_IMAGES % {"org": args.org}

    count = 0
    while next_page is not None:
        resp = requests.get(next_page)
        count += 1
        next_page = None

        if resp.status_code == 200:
            data = resp.json()
            # Read image data
            for img in data['results']:
                # request an overview markdown file for the image
                create_overview(img['name'], args.template_base)
            if data['next'] is not None:
                next_page = data['next']

def process_offline(args):
    template_dir = f'./image-overview-templates/{args.template_base}'
    try:
        for filename in os.listdir(template_dir):
            image_name = filename.replace('.md', '')
            create_overview(image_name, args.template_base)
    except FileNotFoundError as ex:
        print(f"No template dir found: {template_dir}")
        raise ex

# ------------------


def main():
    """ main method
    """
    try:
        args = get_args()
        if args.offline:
            process_offline(args)
        else:
            process_online(args)

    except Exception as ex:
        print(ex)
        sys.exit(-1)


if __name__ == '__main__':  # pragma: no cover

    main()


