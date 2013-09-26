
def test():
	"""Tests for the existence of the ansible program."""
	print "...Checking if ansible is installed..."
	try:
		import ansible
	except ImportError:
		raise Exception('\tAnsible is missing. Install it.')
	print "\tansible is installed, checking version..."
	# test the version of ansible, we are aiming to require greater than or equal to 1.2.2
	from distutils.version import StrictVersion
	minimum_version = "1.2.2"
	if StrictVersion(ansible.__version__) < StrictVersion(minimum_version):
		raise Exception('\tansible is installed, but version is less than', minimum_version)
	# all good.
	print "\tansible version is greater than or equal to", minimum_version
