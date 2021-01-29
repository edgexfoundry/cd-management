<<<<<<< HEAD
# cd-management

This repository contains various tools that facilitate EdgeXfoundry continuous deployment release capabilities and post deployment operations.

Tool | Summary
--- | ---
[changelog-generator](https://github.com/edgexfoundry/cd-management/tree/changelog-generator) | repository changelog management
[create-github-release](https://github.com/edgexfoundry/cd-management/tree/create-github-release) | create GitHub releases with assets
[create-repo-badges](https://github.com/edgexfoundry/cd-management/tree/create-repo-badges) | create badges for all repos
[docker-cis-benchmark](https://github.com/edgexfoundry/cd-management/tree/docker-cis-benchmark) | execute Docker CIS benchmark
[dockerhub-audit](https://github.com/edgexfoundry/cd-management/tree/dockerhub-audit) | audit DockerHub for stale or outdated Docker images
[edgex-compose-builder](https://github.com/edgexfoundry/cd-management/tree/edgex-compose-builder) | update compose builder files with latest versions
[edgex-docker-hub-documentation](https://github.com/edgexfoundry/cd-management/tree/edgex-docker-hub-documentation) | update DockerHub descriptions and overviews
[edgex-go-daily-snap](https://github.com/edgexfoundry/cd-management/tree/edgex-go-daily-snap) | build Snap bundle for `edgex-go`
[edgex-snyk-weekly](https://github.com/edgexfoundry/cd-management/tree/edgex-snyk-weekly) | execute weekly Snyk scans for selected Docker images in Nexus
[git-label-sync](https://github.com/edgexfoundry/cd-management/tree/git-label-sync) | sync GitHub repo labels and milestones
[prune-github-tags](https://github.com/edgexfoundry/cd-management/tree/prune-github-tags) | remove old pre-release tags from GitHub repos
[release](https://github.com/edgexfoundry/cd-management/tree/release) | continuous delivery release automaton
[release-lts](https://github.com/edgexfoundry/cd-management/tree/release-lts) | continuous delivery release automaton for long term support (LTS)
[seed-jenkins-job](https://github.com/edgexfoundry/cd-management/tree/seed-jenkins-jobs) | seed Jenkins server with jobs
=======
# edgex-docker-hub-documentation

## Summary

EdgeX Foundry Docker Hub descriptions and overviews.

Also includes Python3 scripts to:
* generate the overviews from markdown files
* update the description of the associated Docker images in DockerHub

## Jenkins Triggers

Refers to the `deploy-overviews` script only.

* Manual (User initiated)

## Script Usage

### `deploy-overviews`
```bash
usage: deploy-overviews.py [-h] [--overviews OVERVIEWS_PATH]
                           [--descriptions DESCRIPTIONS_PATH] [--user USER]
                           [--name NAME] [--execute]

A Python script that updates descriptions of DockerHub images using a folder
containing associated markdown files

optional arguments:
  -h, --help            show this help message and exit
  --overviews OVERVIEWS_PATH
                        folder path containing Docker image overviews in md
                        format
  --descriptions DESCRIPTIONS_PATH
                        path to file containing Docker image descriptions
  --user USER           DockerHub user containing the Docker images to update
  --name NAME           a regex to match name of images to include in
                        processing
  --execute             execute processing - not setting is same as running in
                        NOOP mode
```
>>>>>>> Add script to deploy overviews to DockerHub
