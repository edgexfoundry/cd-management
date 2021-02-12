# cd-management/edgex-snyk-weekly

## Summary

We want to avoid running Snyk docker scans each time code is merged to main branch, as it quickly uses up 200 scans allowed in the free usage plan.
Instead , we are going to run the scan weekly on the nexus images through this job.

This job will process the list of predefined images in nexus docker repository, make use of `edgeXSnyk` global pipeline library to run the snyk scans on them.

