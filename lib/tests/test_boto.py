#!/usr/bin/env python

print "Checking if boto is installed..."

try:
	import boto
except ImportError:
	print "Python library boto is not installed."
	exit(1)

print "boto is installed, checking version..."

# test the version of boto, we are aiming to require greater than or equal to 2.8.0
from distutils.version import StrictVersion

minimum_version = "2.8.0"

if StrictVersion(boto.__version__) < StrictVersion(minimum_version):
	print "Boto is intalled but is less than", minimum_version
	exit(1)

# all good.
print "boto version is greater than", minimum_version
exit(0)