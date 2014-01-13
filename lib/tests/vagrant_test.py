import util


def library_test():
    """Tests for the existence of the vagrant python library."""
    minimum_version = "0.4.0"
    util.module_version_check(minimum_version, "vagrant", "python-vagrant")


def executable_test():
    import vagrant
    import os
    import subprocess
    command = vagrant.VAGRANT_EXE, "--version"
    version = subprocess.check_output(command, cwd=os.getcwd())
    minimum_version = "1.3.3"
    current_version = version.strip().split(" ")[1]
    util.compare_versions(minimum_version, current_version, "vagrant binary")


def test():
    library_test()
    executable_test()