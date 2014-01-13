import util


def test():
    """Tests for the existence of the boto library."""
    minimum_version = "2.8.0"
    util.module_version_check(minimum_version, "boto")