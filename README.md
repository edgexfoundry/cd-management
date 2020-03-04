# cd-management/git-label-sync

## Summary

This job will sync **ALL** labels from a source Organization/Repository to **ALL** repositories under that certain GitHub Organization. A blacklist argument can be used to exclude labeling of certain repositories within the Source Organization.

## Use Case

A user has a GitHub repo `edgexfoundry/my-template` where they manage a master list of labels. They now want to copy ALL the labels found in  want `edgexfoundry/my-template` to ALL repositories under the `edgexfoundry` org.

## Triggers

* Manual (User initiated)
* Cron (Weekly)

## Script Usage

### github-copy-label.sh

#### Env Vars

* GH_TOKEN_PSW (Required) - The GitHub personal access token used to authenticate GitHub Commands
* GH_BASE_URL (Optional) - GitHub API URL. Can be changed to point to a different GitHub API endpoint i.e. GitHub Enterprise

```Script
./github-copy-label.sh [SRC_GITHUB_ORG] [SRC_GITHUB_REPO] [BLACKLIST_REPOS]
```

#### Example

```Script
export GH_TOKEN_PSW=***************************
./github-copy-label.sh "edgexfoundry" "my-template" "ci-management|sample-service"
```
