#! /usr/bin/env python
# encoding: utf-8

def check(ctx):
	print('Looking for dependencies...')
	from lib.tests import boto_test
	from lib.tests import ansible_test
	try:
		boto_test.test()
		ansible_test.test()
	except Exception as inst:
			print inst.args

