$$./common/warning.md

$$./common/archived-warning.md

$$./common/quick-reference.md

# Supported tags and respective Dockerfile links

$$./common/version-hanoi.md
        - [Dockerfile](https://github.com/edgexfoundry/edgex-go/blob/hanoi/cmd/security-secretstore-setup/Dockerfile)

# Quick reference (cont.)

- Where to file issues: https://github.com/edgexfoundry/edgex-go/issues (NOTE - this image is archived and issues are no longer being worked)

- Supported architectures: arm64

- Published image artifact details: https://nexus3.edgexfoundry.org

- Source of this description: https://github.com/edgexfoundry/edgex-docker-hub-documentation

$$./common/what-is-edgex.md

# What's in this image?

**ARCHIVED**
This image contains the **ARM64 version** of EdgeX security-secretstore-setup service (aka edgex-vault-worker). The container relies on the security-secrets-setup container to create the PKI, in which the requirements of TLS in a single box are no more. security-secretstore-setup service also fork/execs security-file-token-provider to create the tokens, and adds shared secrets to Vault itself.  It was replaced by [docker-security-secretstore-setup-go](https://hub.docker.com/r/edgexfoundry/docker-security-secretstore-setup-go).  It is no longer used or supported.

The service source code: https://github.com/edgexfoundry/edgex-go

$$./common/license.md
[source repository](https://github.com/edgexfoundry/edgex-go/blob/hanoi/cmd/security-secretstore-setup/Attribution.txt).