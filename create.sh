#!/bin/bash

FOLDER_NAME=${1:-FOLDER_NAME}

if [ -z "$JENKINS_USER_ID" ]; then
  echo "Please supply JENKINS_USER_ID env var"
  exit 1
fi

if [ -z "$JENKINS_API_TOKEN" ]; then
  echo "Please supply JENKINS_USER_ID env var"
  exit 1
fi

# create surrounding folder with all pipeline libraries
curl -s -XPOST "https://jenkins.edgexfoundry.org/sandbox/createItem?name=${FOLDER_NAME}" \
  -u "$JENKINS_USER_ID:$JENKINS_API_TOKEN" \
  --data-binary @edgexfoundry-folder.xml \
  -H "Content-Type:text/xml"

# embed GitHub org within folder
curl -s -XPOST "https://jenkins.edgexfoundry.org/sandbox/view/All/job/${FOLDER_NAME}/createItem?name=edgexfoundry" \
  -u "$JENKINS_USER_ID:$JENKINS_API_TOKEN" \
  --data-binary @edgexfoundry-org.xml \
  -H "Content-Type:text/xml"

exit 0