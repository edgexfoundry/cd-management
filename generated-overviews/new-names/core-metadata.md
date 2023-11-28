<!--

********************************************************************************

WARNING:

    DO NOT EDIT.  THIS FILE IS AUTO-GENERATED

********************************************************************************

-->

# Quick reference

- Maintained by: [EdgeX Foundry](https://www.edgexfoundry.org) (a [Linux Foundation](https://www.linuxfoundation.org/) project)

- Where to get help: [EdgeX Web Site](https://www.edgexfoundry.com), [EdgeX Documentation](https://docs.edgexfoundry.com), [EdgeX Slack](https://edgexfoundry.slack.com/), [EdgeX Project Wiki](https://wiki.edgexfoundry.org)

# Supported tags and respective Dockerfile links

- Napa
    - 3.1.0        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v3.1.0/cmd/core-metadata/Dockerfile)
- Minnesota
    - 3.0.0        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v3.0.0/cmd/core-metadata/Dockerfile)
- Levski
    - 2.3.0        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.3.0/cmd/core-metadata/Dockerfile)
- Kamakura
    - 2.2.0        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.2.0/cmd/core-metadata/Dockerfile)
- Jakarta ([LTS](https://wiki.edgexfoundry.org/pages/viewpage.action?pageId=69173332))
    - 2.1.0        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.1.0/cmd/core-metadata/Dockerfile)
- Ireland
    - 2.0.0        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.0.0/cmd/core-metadata/Dockerfile)

# Quick reference (cont.)

- Where to file issues: <https://github.com/edgexfoundry/edgex-go/issues>

- Supported architectures: intel/amd64

- Published image artifact details: <https://nexus3.edgexfoundry.org>

- Source of this description: <https://github.com/edgexfoundry/cd-management/tree/edgex-docker-hub-documentation/image-overview-templates>

# What is EdgeX Foundry?

EdgeX Foundry is a vendor-neutral, open source project hosted by The Linux Foundation building a common open framework for IoT edge computing.  At the heart of the project is an interoperability framework hosted within a full hardware and OS agnostic reference software platform to enable an ecosystem of plug-and-play components that unifies the marketplace and accelerates the deployment of IoT solutions.

In simple terms, EdgeX is edge middleware - serving between physical sensing and actuating "things" and our information technology (IT) systems.

EdgeX's official documentation can be found at [docs.edgexfoundry.org](https://docs.edgexfoundry.org).

![logo](https://www.lfedge.org/wp-content/uploads/2020/11/Screen-Shot-2019-10-28-at-3.45.29-PM-300x269.png)

*Edgey - the official EdgeX Foundry project mascot*

# What's in this image?

This image contains the [core meta data](https://docs.edgexfoundry.org/2.0/microservices/core/metadata/Ch-Metadata/) service and all of its base configuration.

The core metadata micro service has the knowledge about the devices and sensors and how to communicate with them used by the other services, such as core data, core command, and so forth.

Specifically, metadata has the following abilities:

- Manages information about the devices connected to, and operated by, EdgeX Foundry
- Knows the type, and organization of data reported by the devices
- Knows how to command the devices

Although metadata has the knowledge, it does not do the following activities:

- It is not responsible for actual data collection from devices, which is performed by device services and core data
- It is not responsible for issuing commands to the devices, which is performed by core command and device services

The core meta data service source code: <https://github.com/edgexfoundry/edgex-go>

# License

View [license information](https://docs.edgexfoundry.org/latest/#apache-2-license) for the software contained in this image.

As with all Docker images, these likely also contain other software which may be under other licenses (such as Bash, etc from the base distribution, along with any direct or indirect dependencies of the primary software being contained).

As for any pre-built image usage, it is the image user's responsibility to ensure that any use of this image complies with any relevant licenses for all software contained within.

Some additional license information which was able to be auto-detected might be found in the Attribution.txt file located in the image and copied from the associated



