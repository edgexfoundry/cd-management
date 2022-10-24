$$./common/warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-hanoi.md
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/hanoi/cmd/core-metadata/Dockerfile)

$$./common/quick-reference-cont-edgex-go-arm.md

$$./common/what-is-edgex.md

# What's in this image?

This image contains the **ARM64 version** of [core meta data](https://docs.edgexfoundry.org/1.3/microservices/core/metadata/Ch-Metadata/) service and all of its base configuration.

The core metadata micro service has the knowledge about the devices and sensors and how to communicate with them used by the other services, such as core data, core command, and so forth.

Specifically, metadata has the following abilities:

- Manages information about the devices connected to, and operated by, EdgeX Foundry
- Knows the type, and organization of data reported by the devices
- Knows how to command the devices

Although metadata has the knowledge, it does not do the following activities:

- It is not responsible for actual data collection from devices, which is performed by device services and core data
- It is not responsible for issuing commands to the devices, which is performed by core command and device services

The core meta data service source code: https://github.com/edgexfoundry/edgex-go

$$./common/license.md
[source repository](https://github.com/edgexfoundry/edgex-go/blob/hanoi/cmd/core-metadata/Attribution.txt).