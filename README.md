# cd-management/release

## Summary

This job will release artifacts from the main repositories in the EdgeX Foundry Github organization. This job is targeted at releasing artifacts associated with the `master` branch of those repositories. In this branch there are YAML files inside the release folder that describe the artifacts to release for each repository.

## Use Case

At the end of a release cycle for EdgeX Foundry there is series of final steps to release artifacts for the project. This job is aimed at automating as much of these final steps as possible. 

## Triggers

* The job will trigger on merged changes into the `release` branch, the branch this job lives in. 
* This job also checks to see if the YAML file has changed. If there are no changes to the YAML file then that specific repository's artifacts will be not triggered for release.
* During the pull request stage the job will lint the YAML files and print out the release information in the Jenkins logs.

## Usage

* The EdgeX Release Tsar will make changes in the YAML files to release artifacts for release. These changes will be in a seperate branch and a PR will be created against this branch. Once those changes are merged, the release job will be triggered.