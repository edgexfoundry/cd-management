$$./common/warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-kamakura.md |
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.2.0/cmd/support-notifications/Dockerfile)
$$./common/version-jakarta-lts.md |
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.1.0/cmd/support-notifications/Dockerfile)
$$./common/version-ireland.md |
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.0.0/cmd/support-notifications/Dockerfile)

$$./common/quick-reference-cont-edgex-go-arm.md

$$./common/what-is-edgex.md

# What's in this image?

This image contains the **ARM64 version** [support notifications](https://docs.edgexfoundry.org/2.0/microservices/support/notifications/Ch-AlertsNotifications/) service and all of its base configuration.

When another system or a person needs to know that something occurred in EdgeX, the alerts and notifications micro service sends that notification. Examples of alerts and notifications that other services could broadcast, include the provisioning of a new device, sensor data detected outside of certain parameters (usually detected by a device service or rules engine) or system or service malfunctions (usually detected by system management services).

The support notifications service source code: <https://github.com/edgexfoundry/edgex-go>

$$./common/license.md
[source repository](https://github.com/edgexfoundry/edgex-go/blob/v2.2.0/Attribution.txt).
