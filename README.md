[![License BSD-2-Clause](https://img.shields.io/badge/License-BSD--2--Clause-blue.svg)](https://opensource.org/licenses/BSD-2-Clause)
[![License MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# ezsetup
Welcome to `ezsetup` 🎉

`ezsetup` is a single-file el-cheapo installer which offers basic features like downloading, checksum verification,
tarball extraction and build/install/uninstall command execution.

## Why?
`ezsetup` offers a simple building block which can be used in more complex workflows like ansible deployments etc.

## Package format
Each package is a simple tarball which contains two scripts:
 - `install.sh` to build and install the package
 - `uninstall.sh` to uninstall the package
  
### Verifiable URIs
Packages are referenced by special URI format `sha256=<hex digest...>=<tarball url...>`, where `hex digest...` is the
hex-encoded SHA2-256 digest of the tarball. This allows the user to pin a specific tarball, which can be useful if you
are downloading from an untrusted source.
