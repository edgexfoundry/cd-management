$$./common/warning.md

$$./common/archived-warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-barcelona.md |
        - [Dockerfile](https://github.com/edgexfoundry/core-command/blob/barcelona/docker-files/Dockerfile)

# Quick reference (cont.)

- Where to file issues: https://github.com/edgexfoundry/core-command/issues (NOTE - this image is archived and issues are no longer being worked)

- Supported architectures: intel/amd64

- Published image artifact details: https://nexus3.edgexfoundry.org

- Source of this description: https://github.com/edgexfoundry/cd-management/tree/edgex-docker-hub-documentation

$$./common/what-is-edgex.md

# What's in this image?

**ARCHIVED**
This image contains the legacy Java [core command](https://docs.edgexfoundry.org/1.3/microservices/core/command/Ch-Command/) service and all of its base configuration.

The command micro service (often called the command
and control micro service) enables the issuance of commands or actions to
devices on behalf of:

-   other micro services within EdgeX Foundry (for example, an edge
    analytics or rules engine micro service)
-   other applications that may exist on the same system with EdgeX
    Foundry (for example, a management agent that needs to
    shutoff a sensor)
-   To any external system that needs to command those devices (for
    example, a cloud-based application that determined the need to
    modify the settings on a collection of devices)

The command micro service exposes the commands in a common, normalized
way to simplify communications with the devices. There are two types of commands that can be sent to a device.

- a GET command requests data from the device.  This is often used to request the latest sensor reading from the device.
- PUT commands request to take action or actuate the device or to set some configuration on the device.

The core data service source code: https://github.com/edgexfoundry/core-command

$$./common/license.md
[source repository](https://github.com/edgexfoundry/core-command/blob/barcelona/Attribution.txt).