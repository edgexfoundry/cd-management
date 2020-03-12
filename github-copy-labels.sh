#! /bin/bash
# https://douglascayers.com/2019/08/01/how-to-export-and-import-github-issue-labels-between-projects/

set -e

GH_BASE_URL=${GH_BASE_URL:-https://api.github.com}
GH_TOKEN=${GH_TOKEN_PSW}

# The source repository whose labels to copy.
SRC_GH_ORG=$1
SRC_GH_REPO=$2
BLACKLIST_REPOS=$3 #optional

usage() {
  echo "This script will copy ALL labels from the source GitHub Org/Repo to ALL repos within the source Org"
  echo
  echo "Usage: $0 [Source GitHub Org] [Source GitHub Repo]"
  echo "Example: $0 edgexfoundry github-label-template-repo"
}

if [ -z "$SRC_GH_ORG" ]; then
  usage
  exit 1
fi

if [ -z "$SRC_GH_REPO" ]; then
  usage
  exit 1
fi

# Headers used in curl commands
GH_ACCEPT_HEADER="Accept: application/vnd.github.symmetra-preview+json"
GH_AUTH_HEADER="Authorization: Bearer $GH_TOKEN"

# ---------------------------------------------------------

getAllTargetRepos() {
  all_repos=$(curl --silent -H "$GH_ACCEPT_HEADER" -H "$GH_AUTH_HEADER" "$GH_BASE_URL/orgs/$SRC_GH_ORG/repos?per_page=200" | jq -r '.[] | select((.archived = false) and .disabled = false) | .name')

  # filter out based on BLACKLIST_REPOS and always filter the src repo
  if [ -z "$BLACKLIST_REPOS" ]; then
    echo "$all_repos" | egrep -v "$SRC_GH_REPO"
  else
    echo "$all_repos" | egrep -v "$SRC_GH_REPO|$BLACKLIST_REPOS"
  fi
}

getSourceLabels() {
  curl --silent -H "$GH_ACCEPT_HEADER" -H "$GH_AUTH_HEADER" "$GH_BASE_URL/repos/${SRC_GH_ORG}/${SRC_GH_REPO}/labels" | jq '[ .[] | { "name": .name, "color": .color, "description": .description } ]' | jq -r '.[] | @base64'
}

tagTargetReposWithLabel() {
  # $1 => Target Org
  # $2 => Target Repo
  # $3 => Source label json

  # base64 decode the json
  sourceLabelJson=$(echo $3 | base64 --decode | jq -r '.')
  labelName=$(echo $sourceLabelJson | jq -r '.name')

  # try to create the label
  # POST /repos/:owner/:repo/labels { name, color, description }
  # https://developer.github.com/v3/issues/labels/#create-a-label
  createLabelResponse=$(echo $sourceLabelJson | curl --silent -X POST -d @- -H "$GH_ACCEPT_HEADER" -H "$GH_AUTH_HEADER" "$GH_BASE_URL/repos/$1/$2/labels")

  # if creation failed then the response doesn't include an id and jq returns 'null'
  createdLabelId=$(echo $createLabelResponse | jq -r '.id')

  # if label wasn't created maybe it's because it already exists, try to update it
  if [ "${createdLabelId}" == "null" ]; then
      updateLabelResponse=$(echo $sourceLabelJson | curl --silent -X PATCH -d @- -H "$GH_ACCEPT_HEADER" -H "$GH_AUTH_HEADER" "$GH_BASE_URL/repos/$1/$2/labels/$(echo $sourceLabelJson | jq -r '.name | @uri')")
      responseMessage=$(echo $updateLabelResponse | jq -r '.id')
      
      if [ "${responseMessage}" == "null" ]; then
        errorMessage=$(echo $updateLabelResponse | jq -r '.message + ": " + .documentation_url')
        echo "[github-copy-labels] Unable to create label [$labelName] in [$1/$2]. GitHub Error: ${errorMessage}."
      else
        echo "[github-copy-labels] Successfully updated new label [$labelName] in [$1/$2]."
      fi
  else
      echo "[github-copy-labels] Successfully created new label [$labelName] in [$1/$2]. LabelId: $createdLabelId"
  fi
}

sourceLabels=$(getSourceLabels)
sourceLabelsCsv=$(csv=""; for label in $sourceLabels; do token=$(echo "$label" | base64 --decode | jq -r '.name'); csv="${csv}${csv:+,} $token"; done; echo $csv)

# for each label from source repo, invoke github api to create or update the label in the target repo
for targetRepo in $(getAllTargetRepos); do
  echo "[github-copy-labels] About to tag the following target repo [$SRC_GH_ORG/$targetRepo] with labels [$sourceLabelsCsv]"
  echo
  for labelJsonB64 in $sourceLabels; do
    tagTargetReposWithLabel "$SRC_GH_ORG" "$targetRepo" $labelJsonB64
  done
  echo
done