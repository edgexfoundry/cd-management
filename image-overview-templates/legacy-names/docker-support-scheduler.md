$$./common/warning.md

$$./common/archived-warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-california.md |
        - [Dockerfile](https://github.com/edgexfoundry/support-scheduler/blob/california/docker-files/Dockerfile)

# Quick reference (cont.)

- Where to file issues: https://github.com/edgexfoundry/support-scheduler/issues (NOTE - this image is archived and issues are no longer being worked)

- Supported architectures: intel/amd64

- Published image artifact details: https://nexus3.edgexfoundry.org

- Source of this description: https://github.com/edgexfoundry/cd-management/tree/edgex-docker-hub-documentation

$$./common/what-is-edgex.md

# What's in this image?

**ARCHIVED**
This image contains the legacy Java [support scheduler](https://docs.edgexfoundry.org/1.2/microservices/support/scheduler/Ch-Scheduling/) service and all of its base configuration.

The support scheduler micro service provide an internal EdgeX “clock” that can kick off operations in any EdgeX service. At a configuration specified time (called an interval), the service calls on any EdgeX service API URL via REST to trigger an operation (called an interval action).

The support scheduler service source code: https://github.com/edgexfoundry/support-scheduler

$$./common/license.md
[source repository](https://github.com/edgexfoundry/support-scheduler/blob/california/Attribution.txt).