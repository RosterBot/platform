
def test():
	"""Tests for the existence of the boto library."""
	print "...Checking if boto is installed..."
	try:
		import boto
	except ImportError:
		raise Exception('\tboto is missing. Install it.')
	print "\tboto is installed, checking version..."
	# test the version of boto, we are aiming to require greater than or equal to 2.8.0
	from distutils.version import StrictVersion
	minimum_version = "2.8.0"
	if StrictVersion(boto.__version__) < StrictVersion(minimum_version):
		raise Exception('\tboto is installed, but version is less than', minimum_version)
	# all good.
	print "\tboto version is greater than or equal to", minimum_version