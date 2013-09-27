import util

def test():
	"""Tests for the existence of the ansible program."""
	minimum_version = "1.2.2"
	util.module_version_check(minimum_version, "ansible")
