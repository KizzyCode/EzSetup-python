#!/usr/bin/env python3

import hashlib
import os
import os.path
import subprocess
import sys
import tarfile
import tempfile
import urllib.request


class UriResource:
    """An URI resource with builtin fetch functionality and checksum verification"""

    _algo = None
    """The verification algorithm"""

    _tag = None
    """The verification tag"""

    _url = None
    """The URL"""

    def __init__(self, uri):
        """Creates a new resource fetcher for the given URI"""
        # Split the resource
        segments = uri.split("=", 2)
        if len(segments) != 3:
            raise RuntimeError(f"Invalid resource location: { uri }")
        
        # Init self
        self._algo = segments[0]
        self._tag = segments[1]
        self._url = segments[2]
    
    def fetch(self):
        """Fetches and verifies the data"""
        data = urllib.request.urlopen(self._url).read()
        self._verify(data)
        return data

    def _verify(self, data):
        """Verifies some data against the tag"""
        if self._algo == "none":
            return
        elif self._algo == "sha256":
            self._verifier_sha256(data)
        else:
            raise RuntimeError(f"Unexpected verifier algorithm (got { self._algo })")

    def _verifier_sha256(self, data):
        """Verifies a SHA-256 digest"""
        # Compute the hash
        sha256 = hashlib.sha256()
        sha256.update(data)
        tag = sha256.hexdigest()

        # Validate the digest
        if tag != self._tag:
            raise RuntimeError(f"Unexpected checksum (expected { self._tag }; got { tag })")


class Script:
    """A task to execute a script"""

    _script = None
    """The script to execute"""

    def __init__(self, script):
        """Creates a script task"""
        self._script = script
    
    def exec(self, cwd):
        """Executes the script"""
        result = subprocess.run(self._script, capture_output=False, shell=True, cwd=cwd, env=os.environ)
        result.check_returncode()


class Package:
    """A package"""

    _uri = None
    """The tarball URL"""

    _tempfile = None
    """The temporary file"""

    _tempdir = None
    """The temporary dir"""

    _srcdir = None
    """The source directory"""

    def __init__(self, uri):
        """Initializes the package"""
        self._uri = uri
        self._tempfile = tempfile.TemporaryFile()
        self._tempdir = tempfile.TemporaryDirectory()

    def fetch(self):
        """Downloads, verifies and extracts the tarball; returns a handle to `self` for method chaining"""
        # Fetch the tarball
        tarball_data = UriResource(self._uri).fetch()
        self._tempfile.write(tarball_data)
        self._tempfile.seek(0)
        
        # Extract archive and find sourcedir
        tarball = tarfile.open(fileobj=self._tempfile)
        tarball.extractall(path=self._tempdir.name)
        self._srcdir = self._find_srcdir()
        return self
    
    def install(self):
        """Builds and installs the package"""
        install_sh = self._make_path("install.sh")
        Script(install_sh).exec(self._srcdir)

    def uninstall(self):
        """Uninstalls the package"""
        uninstall_sh = self._make_path("uninstall.sh")
        Script(uninstall_sh).exec(self._srcdir)
    
    def _find_srcdir(self):
        # List the toplevel entries within the package
        entries = os.listdir(self._tempdir.name)
        if len(entries) < 1:
            raise RuntimeError("Packaged archive has no contents")
        
        # Check if the tar archive is flat
        if "install.sh" in entries and "uninstall.sh" in entries:
            return self._tempdir.name
        
        # Find the first top-level directory which contains both "install.sh" and "uninstall.sh"
        paths = map(lambda entry: os.path.join(self._tempdir.name, entry), entries)
        for directory in filter(os.path.isdir, paths):
            subentries = os.listdir(directory)
            if "install.sh" in subentries and "uninstall.sh" in subentries:
                return directory
        
        # Package is invalid
        raise RuntimeError("Failed to locate package scripts")


    def _make_path(self, entry):
        """Returns the path to `entry` within the source dir"""
        return os.path.join(self._srcdir, entry)


class Cli:
    """The CLI processor"""

    _verb = None
    """The verb"""

    _package = None
    """The package URL"""

    def __init__(self, argv):
        """Initializes the CLI processor with argv"""
        # Validate argv length
        if len(argv) < 3:
            self._help(errorneous=True)
        
        # Init self
        self._verb = argv[1]
        self._package = argv[2]
    
    def exec(self):
        """Executes the command"""
        if self._verb == "install":
            Package(self._package).fetch().install()
        elif self._verb == "uninstall":
            Package(self._package).fetch().uninstall()
        elif self._verb == "help":
            Cli._help()
        else:
            Cli._help(errorneous=True)
    
    @classmethod
    def _help(cls, errorneous=False):
        """Displays the help and exits"""
        # Display the help
        text = \
f"""
Usage: { sys.argv[0] } install|uninstall package
    
    install: Installs the given package
    uninstall: Uninstalls the given package
    package: The package URI in the format `sha256=hexdigest=url`
"""
        print(text)

        # Exit with the appropriate error code
        if errorneous:
            sys.exit(1)
        else:
            sys.exit(0)


# Execute ezsetup
if __name__ == "__main__":
    Cli(sys.argv).exec()
