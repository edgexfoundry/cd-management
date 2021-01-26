$$./common/warning.md

$$./common/archived-warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-barcelona.md
        - [Dockerfile](https://github.com/edgexfoundry/core-metadata/blob/barcelona/docker-files/Dockerfile)

# Quick reference (cont.)

- Where to file issues: https://github.com/edgexfoundry/core-metadata/issues (NOTE - this image is archived and issues are no longer being worked)

- Supported architectures: intel/amd64

- Published image artifact details: https://nexus3.edgexfoundry.org

- Source of this description: https://github.com/edgexfoundry/edgex-docker-hub-documentation

$$./common/what-is-edgex.md

# What's in this image?

**ARCHIVED**
This image contains the legacy Java [core metadata](https://docs.edgexfoundry.org/1.3/microservices/core/metadata/Ch-Metadata/) service and all of its base configuration.

The core data micro service provides centralized persistence for data collected by devices. Device services that collect sensor data call on the core data service to store the sensor data on the edge system (such as in a gateway) until the data gets moved "north" and then exported to Enterprise and cloud systems. Core data persists the data in a local database. Redis is used by default, but a database abstraction layer allows for other databases to be used.

The core data service source code: https://github.com/edgexfoundry/core-metadata

$$./common/license.md
[source repository](https://github.com/edgexfoundry/core-metadata/blob/barcelona/Attribution.txt).