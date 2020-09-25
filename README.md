# seed-jenkins-jobs

## Summary

Seed jenkins server with jobs.

Currently the [create.sh](./create.sh) script will create a top level folder in the All view. This top level folder will be configured with edgex-global-pipelines and lf-pipelines global libraries. Inside that folder you will find a GitHub project named edgexfoundry which you can scan to create the rest of the jobs.

## Folder Structure

```Text
- <Your Folder>
  |
  __ edgexfoundry
  |____ repo 1
  |____ repo 2
  ...
  |____ repo n
```

## Usage

Note: An Jenkins authentication token will need to be generated on the Jenkins server before running this script. The authentication ENV vars will need to be set before running this script. Jenkins tokens can be created on your user configuration page found here: `JENKINS_URL/me/configure`.

```Bash
export JENKINS_USER=your-username
export JENKINS_API_TOKEN=***********************

./create.sh "My-Fun-Folder"
```
