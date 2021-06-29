$$./common/warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-ireland.md |
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.0.0/cmd/support-scheduler/Dockerfile)

$$./common/quick-reference-cont-edgex-go-arm.md

$$./common/what-is-edgex.md

# What's in this image?

This image contains the **ARM64 version** [support scheduler](https://docs.edgexfoundry.org/2.0/microservices/support/scheduler/Ch-Scheduling/) service and all of its base configuration.

The support scheduler micro service provide an internal EdgeX “clock” that can kick off operations in any EdgeX service. At a configuration specified time (called an interval), the service calls on any EdgeX service API URL via REST to trigger an operation (called an interval action).

The support scheduler service source code: <https://github.com/edgexfoundry/edgex-go>

$$./common/license.md
[source repository](https://github.com/edgexfoundry/edgex-go/blob/v2.0.0/cmd/support-scheduler/Attribution.txt).
