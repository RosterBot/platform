import util

def test():
    """Tests for the existence of the ansible program."""
    minimum_version = "1.4.0"
    util.module_version_check(minimum_version, "ansible")
