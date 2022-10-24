$$./common/warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-kamakura.md |
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.2.0/cmd/sys-mgmt-agent/Dockerfile)
$$./common/version-jakarta-lts.md |
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.1.0/cmd/sys-mgmt-agent/Dockerfile)
$$./common/version-ireland.md |
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.0.0/cmd/sys-mgmt-agent/Dockerfile)

$$./common/quick-reference-cont-edgex-go-arm.md

$$./common/what-is-edgex.md

# What's in this image?

This image contains the **ARM64 version** [system management agent](https://docs.edgexfoundry.org/2.0/microservices/system-management/Ch_SystemManagement/) and all of its base configuration.

The SMA is micro service that other systems or services communicate with and make their management request (to start/stop/restart, get the configuration, get the status/health, or get metrics of the EdgeX service). It communicates with the EdgeX micro services or executor to satisfy the requests. The SMA serves as the connection point of management control for an EdgeX instance.

The system management agent source code: <https://github.com/edgexfoundry/edgex-go>

$$./common/license.md
