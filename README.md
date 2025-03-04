# cd-management
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr-raw/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/pulls) 
[![GitHub Contributors](https://img.shields.io/github/contributors/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/contributors) 
[![GitHub Committers](https://img.shields.io/badge/team-committers-green)](https://github.com/orgs/edgexfoundry/teams/devops-core-team/members) 
[![GitHub Commit Activity](https://img.shields.io/github/commit-activity/m/edgexfoundry/cd-management)](https://github.com/edgexfoundry/cd-management/commits)

Automated GitHub Action to create a multi-arch docker image for each EdgeX Foundry service.

- Iterates through **repos** defined in the config.json.
- Pull or create image with AMD64 tag.
- Pull ARM64 image.
- Create and Push docker manifests with AMD64 and ARM64 images

---

Note: 
This workflow is triggered by pushing new commits containing config.json changes to this **build-docker-manifests** branch.
