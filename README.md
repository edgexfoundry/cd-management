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

## config.json Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `version` | string | The image tag version to build (e.g. `"4.0.2"`) |
| `force_rebuild_amd` | boolean | If `true`, delete and rebuild the `-amd64` image even if it already exists on Docker Hub. If `false` (default), skip rebuilding when the tag is already present. |
| `repos` | array | List of Docker Hub repositories to create multi-arch manifests for |

---

Note: 
This workflow is triggered by pushing new commits containing config.json changes to this **build-docker-manifests** branch.
