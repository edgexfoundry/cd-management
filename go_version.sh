#!/bin/bash

# set -x
set +e

git  ls-remote --exit-code --heads origin "refs/heads/$NEW_BRANCH"
if [ $? -eq 2 ]; then
    echo "Attempting to change Go version in Jenkinsfile"
    # checkout new branch
    git checkout -b "$NEW_BRANCH"

    # update go version
    if grep -q "goVersion" Jenkinsfile; then
        # This is a bit crude, but should work for all cases
        echo "Jenkinsfile already contains a goVersion, Updating..."

        go_version=$(grep goVersion Jenkinsfile | cut -d: -f 2)
        sed -i "s/$go_version/ '$GO_VERSION',/g" Jenkinsfile
        cat Jenkinsfile
    else
        echo "Jenkinsfile does not contain goVersion, Pinning..."

        new_block=$(sed 's/^)/    goVersion: '$GO_VERSION'\n)/g' Jenkinsfile | grep -v "//" | grep -v "(\|)" | sed '/^$/d' | sed 's/,$//g' | sed 's/$/,/g')
        block_added=0
        while read line; do
            if echo "${line}" | grep -q ".*: .*"; then
                if [ $block_added -eq 0 ]; then
                    echo "$new_block"
                    block_added=1
                fi
            else
                echo "$line"
            fi
        done <<< "$(cat Jenkinsfile)" > Jenkinsfile.new
        mv Jenkinsfile.new Jenkinsfile
    fi
else
    echo "[$NEW_BRANCH] already exists. Exiting!"
    exit 1
fi