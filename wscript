#! /usr/bin/env python
# encoding: utf-8

def check(ctx):
	"""Check that all dependencies are installed and at least the minimum required version."""
	print('Looking for dependencies...')
	from lib.tests import boto_test
	from lib.tests import ansible_test
	from lib.tests import vagrant_test
	from lib.tests import virtualbox_test
	try:
		boto_test.test()
		ansible_test.test()
		vagrant_test.test()
		virtualbox_test.test()
	except Exception as inst:
		print '\033[0;31m'
		print inst
		print '\033[0m'
		exit(1)
