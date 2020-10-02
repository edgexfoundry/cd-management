[![build-status](https://jenkins.edgexfoundry.org/job/edgexfoundry/job/cd-management/job/git-label-sync/badge/icon)](https://jenkins.edgexfoundry.org/job/edgexfoundry/job/cd-management/job/git-label-sync)

# cd-management/git-label-sync

## Summary

This job will sync **ALL** labels and milestones from a source Organization/Repository to **ALL** repositories under a specified GitHub Organization. A blacklist argument can be used to exclude certain repositories within the Source Organization.

## Use Case

A user has a GitHub repo `edgexfoundry/my-template` where they manage a master list of labels and milestones. They now want to copy ALL the labels and milestones found in `edgexfoundry/my-template` to ALL repositories under the `edgexfoundry` org.

## Jenkins Triggers

* Manual (User initiated)
* Cron (Daily at midnight EST)

## Script Usage

### `githubsync`
```Script
usage: githubsync [-h] [--target-org TARGET_ORG] [--source-repo SOURCE_REPO]
                  [--blacklist-repos BLACKLIST_REPOS] [--procs PROCESSES]
                  [--screen] [--modified-since MODIFIED_SINCE] [--debug]
                  [--noop]

A Python script to synchronize GitHub labels and milestones

optional arguments:
  -h, --help            show this help message and exit
  --target-org TARGET_ORG
                        GitHub organization containing repos that will be the
                        synchronization targets
  --source-repo SOURCE_REPO
                        GitHub repo that is the source of the labels and
                        milestones
  --blacklist-repos BLACKLIST_REPOS
                        a comma-delimited list of repos to exclude from
                        synchronization
  --procs PROCESSES     number of concurrent processes to execute a given process
                        is responsible for synchronizing a single repo
  --screen              execute multi-processing dyynamically update curses
                        screen
  --modified-since MODIFIED_SINCE
                        choose sources that have been modified since the duration
                        provided: #[d|h|m] where d=days, h=hours, m=minutes
  --debug               enable debug mode
  --noop                execute in NOOP mode
```

#### Pseudo-code
```Script
get labels from source repo
get milestones from source repo
get repos from target org (exclude blacklist)

def synchronize:
    for each repo in target org:
        synchronize_resource (labels and milestones)

def synchronize_resource:
    for each resource:
        if resource exists on target repo
            if resource on source repo has been modified since time specified
                modify resource on target repo
            else
                no modification necessary
        else
            create resource on target repo
```

#### Env Vars

* `GH_TOKEN_PSW`       (Required) - The GitHub personal access token used to authenticate GitHub Commands
* `GH_BASE_URL`        (Optional) - GitHub API URL. Can be changed to point to a different GitHub API endpoint i.e. GitHub Enterprise
* `GH_TARGET_ORG`      (Optional) - GitHub target organization
* `GH_SOURCE_REPO`     (Optional) - GitHub repo that is source of labels and milestones
* `GH_BLACKLIST_REPOS` (Optional) - GitHub repos to exclude from synchronization
* `DRY_RUN`            (Optional) - Execute in noop mode - the --noop argument takes precedence

#### Example

```Script
export GH_TOKEN_PSW=*****************************************
export GH_BASE_URL=api.github.com
export GH_TARGET_ORG=edgexfoundry
export GH_SOURCE_REPO=edgexfoundry/cd-management
```

Start `4` concurrent processes with no screen and exclude the specified repos
```Script
githubsync --procs 4 --blacklist-repos 'cd-management,ci-build-images'
```

Start `2` concurrent processes with screen and only include sources that have been modified within the past day and run in NOOP mode
```Script
githubsync --procs 2 --modified-since 1d --noop --screen
```

### Development
Clone the repository:
```
cd
git clone https://github.com/edgexfoundry/cd-management.git sync-github-labels
cd sync-github-labels
```

Build the Docker image:
```
docker image build \
--build-arg http_proxy \
--build-arg https_proxy \
-t \
githubsync:latest .
```

Run the Docker container:
```
docker container run \
--rm \
-it \
-e http_proxy \
-e https_proxy \
-v $PWD:/githubsync \
githubsync:latest \
/bin/sh
```

Execute the build:
```
pyb -X
```
NOTE: commands above assume working behind a proxy, if not then the proxy arguments to both the docker build and run commands can be removed.
