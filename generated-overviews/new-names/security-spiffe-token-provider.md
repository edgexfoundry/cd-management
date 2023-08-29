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

- Minnesota
    - 3.0.0        - [Dockerfile](https://github.com/edgexfoundry/security-spiffe-token-provider/blob/v3.0.0/Dockerfile)
- Levski
    - 2.3.0        - [Dockerfile](https://github.com/edgexfoundry/security-spiffe-token-provider/blob/v2.3.0/Dockerfile)
- Kamakura
    - 2.2.0        - [Dockerfile](https://github.com/edgexfoundry/security-spiffe-token-provider/blob/v2.2.0/Dockerfile)

# Quick reference 

- Where to file issues: https://github.com/edgexfoundry/security-spiffe-token-provider/issues
- Supported architectures: intel/amd64
- Source of this description: https://github.com/edgexfoundry/cd-management/tree/edgex-docker-hub-documentation/image-overview-templates/new-names/security-spiffe-token-provider.md

# What is EdgeX Foundry?

EdgeX Foundry is a vendor-neutral, open source project hosted by The Linux Foundation building a common open framework for IoT edge computing.  At the heart of the project is an interoperability framework hosted within a full hardware and OS agnostic reference software platform to enable an ecosystem of plug-and-play components that unifies the marketplace and accelerates the deployment of IoT solutions.

In simple terms, EdgeX is edge middleware - serving between physical sensing and actuating "things" and our information technology (IT) systems.

EdgeX's official documentation can be found at [docs.edgexfoundry.org](https://docs.edgexfoundry.org).

![logo](https://www.lfedge.org/wp-content/uploads/2020/11/Screen-Shot-2019-10-28-at-3.45.29-PM-300x269.png)

*Edgey - the official EdgeX Foundry project mascot*

# What's in this image?

This image contains a microservice that [enables security for remote device services](https://docs.edgexfoundry.org/2.2/security/Ch-RemoteDeviceServices/)
and delayed-start microservices that cannot have an EdgeX secret token pre-seeded to the microservice.
This service works by exchanging a [SPIFFE](https://spiffe.io/) X.509 SVID for an EdgeX secret store token.
This is necessary when EdgeX is running in security-enabled mode in order to access the EdgeX secret store,
the EdgeX secure message bus, the EdgeX registry provider, and the EdgeX configuration provider services.

Source code for security-spiffe-token-provider: <https://github.com/edgexfoundry/edgex-go/>

# License

View [license information](https://docs.edgexfoundry.org/latest/#apache-2-license) for the software contained in this image.

As with all Docker images, these likely also contain other software which may be under other licenses (such as Bash, etc from the base distribution, along with any direct or indirect dependencies of the primary software being contained).

As for any pre-built image usage, it is the image user's responsibility to ensure that any use of this image complies with any relevant licenses for all software contained within.

Some additional license information which was able to be auto-detected might be found in the Attribution.txt file located in the image and copied from the associated


