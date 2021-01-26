$$./common/warning.md

$$./common/archived-warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-barcelona.md
        - [Dockerfile](https://github.com/edgexfoundry/export-distro/blob/master/docker-files/Dockerfile)

# Quick reference (cont.)

- Where to file issues: https://github.com/edgexfoundry/export-distro/issues (NOTE - this image is archived and issues are no longer being worked)

- Supported architectures: intel/amd64

- Published image artifact details: https://nexus3.edgexfoundry.org

- Source of this description: https://github.com/edgexfoundry/edgex-docker-hub-documentation

$$./common/what-is-edgex.md

# What's in this image?

**ARCHIVED**
This image contains the legacy Java export distribution micro service, also known as “Export Distro.” It receives data from Core Data, through a message queue, then filters, transforms, and formats the data per client request, and then distributes it through REST, MQTT, or 0MQ to client endpoints of choice. This service is used for export of data in older EdgeX Foundry releases.  It is no longer used or supported.

The export distro service source code: https://github.com/edgexfoundry/export-distro

$$./common/license.md
[source repository](https://github.com/edgexfoundry/export-distro/blob/barcelona/Attribution.txt).