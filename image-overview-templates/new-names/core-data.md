$$./common/warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-ireland.md |
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v2.0.0/cmd/core-data/Dockerfile)

$$./common/quick-reference-cont-edgex-go.md

$$./common/what-is-edgex.md

# What's in this image?

This image contains the [core data](https://docs.edgexfoundry.org/2.0/microservices/core/data/Ch-CoreData/) service and all of its base configuration.

The core data micro service provides centralized persistence for data collected by devices. Device services that collect sensor data call on the core data service to store the sensor data on the edge system (such as in a gateway) until the data gets moved "north" and then exported to Enterprise and cloud systems. Core data persists the data in a local database. Redis is used by default, but a database abstraction layer allows for other databases to be used.

The core data service source code: <https://github.com/edgexfoundry/edgex-go>

$$./common/license.md
[source repository](https://github.com/edgexfoundry/edgex-go/blob/v2.0.0/Attribution.txt).
