$$./common/warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-levski.md |
        - [Dockerfile](https://github.com/edgexfoundry/device-virtual-go/blob/v2.3.0/Dockerfile)
$$./common/version-kamakura.md |
        - [Dockerfile](https://github.com/edgexfoundry/device-virtual-go/blob/v2.2.0/Dockerfile)
$$./common/version-jakarta-lts.md |
        - [Dockerfile](https://github.com/edgexfoundry/device-virtual-go/blob/v2.1.0/Dockerfile)
$$./common/version-ireland.md |
        - [Dockerfile](https://github.com/edgexfoundry/device-virtual-go/blob/v2.0.0/Dockerfile)

# Quick reference

- Where to file issues: https://github.com/edgexfoundry/device-virtual-go/issues
- Supported architectures: intel/amd64
- Source of this description: https://github.com/edgexfoundry/cd-management/tree/edgex-docker-hub-documentation/image-overview-templates/new-names/device-virtual.md

$$./common/what-is-edgex.md

# What's in this image?

This image contains the [virtual device service](https://docs.edgexfoundry.org/2.0/microservices/device/virtual/Ch-VirtualDevice/), which simulates different kinds of devices to generate events and readings to the core data micro service, and users send commands and get responses through the command and control micro service. These features of the virtual device services are useful when executing functional or performance tests without having any real devices.

The device virtual service source code: <https://github.com/edgexfoundry/device-virtual-go>

$$./common/license.md
