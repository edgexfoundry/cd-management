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
import sys
import requests

DIVIDER = ":"
LIST_IMAGES = 'https://hub.docker.com/v2/repositories/%(org)s/'
DESC_FILE = './descriptions/image_descriptions.txt'
MAX_LEN = 100

def get_file_content(filename):
    content = ""
    # if the content file can be opened, return the content in the file; otherwise specify missing content in markdown
    try:
        f = open(filename, "r")
        content = f.read()
        f.close()
    except FileNotFoundError:
        print("No description file %s" % filename)
    except:
        print("Trouble opening description file %s" % filename)
    return content

def check_desc_length(description, image_name):
    if (len(description)) > MAX_LEN:
        print("\tDescription for %s is TOO LONG (%s)" % (image_name, len(description)))

def get_description(content, loc, image_name):
    begin = loc +1
    end = content.find("\n", loc)
    description = content[begin:end]
    check_desc_length(description, image_name)

def check_existence(content, image_name):
    loc = content.find(image_name+DIVIDER)
    if loc > 0:
        print("Description found for %s" % image_name)
        get_description(content,loc,image_name)
    else:
        print("Description NOT found for %s" % image_name)

# ------------------

org = "edgexfoundry"
if len(sys.argv) > 1:
    org = sys.argv[1]

next_page = LIST_IMAGES % {"org": org}

content = get_file_content(DESC_FILE)
if len(content) <= 0:
    print("Description file is empty or not found; check ending")
else:
    count = 0
    while next_page is not None:
        resp = requests.get(next_page)
        count += 1
        next_page = None
        if resp.status_code == 200:
            data = resp.json()
            # Read project data
            for img in data['results']:
                ## check that the repo has a description in the file
                check_existence(content, img['name'])
            if data['next'] is not None:
                next_page = data['next']
print("Done checking descriptions")

