$$./common/warning.md

$$./common/legacy-note.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-california.md |
        - [Dockerfile](https://github.com/edgexfoundry/support-notifications/blob/barcelona/docker-files/Dockerfile)

# Quick reference (cont.)

- Where to file issues: https://github.com/edgexfoundry/support-notifications/issues (NOTE - this image is archived and issues are no longer being worked)

- Supported architectures: intel/amd64

- Published image artifact details: https://nexus3.edgexfoundry.org

- Source of this description: https://github.com/edgexfoundry/cd-management/tree/edgex-docker-hub-documentation

$$./common/what-is-edgex.md

# What's in this image?

**ARCHIVED**
This image contains the legacy Java [support notifications](https://docs.edgexfoundry.org/1.3/microservices/support/notifications/Ch-AlertsNotifications/) service and all of its base configuration.

When another system or a person needs to know that something occurred in EdgeX, the alerts and notifications micro service sends that notification. Examples of alerts and notifications that other services could broadcast, include the provisioning of a new device, sensor data detected outside of certain parameters (usually detected by a device service or rules engine) or system or service malfunctions (usually detected by system management services).

The support notifications service source code: https://github.com/edgexfoundry/support-notifications

$$./common/license.md
[source repository](https://github.com/edgexfoundry/support-notifications/blob/barcelona/Attribution.txt).