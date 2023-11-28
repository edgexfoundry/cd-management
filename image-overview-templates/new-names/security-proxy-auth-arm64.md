$$./common/warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-napa.md |
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v3.1.0/cmd/security-proxy-auth/Dockerfile)
$$./common/version-minnesota.md |
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/v3.0.0/cmd/security-proxy-auth/Dockerfile)

$$./common/quick-reference-cont-edgex-go.md

$$./common/what-is-edgex.md

# What's in this image?

This image contains the **arm64** version of the service which performs delegated authentication for the NGINX API gateway. It evaluates the incoming JWT on API gateway calls and returns success (HTTP 200) or failure (HTTP 401) to authorize or deny the request from being forwarded to the backend EdgeX microservice.

The service source code: <https://github.com/edgexfoundry/edgex-go>

$$./common/license.md
