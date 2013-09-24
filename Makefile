
# include the platform.conf here to get access to its variables.
SHELL=/bin/bash

.PHONY: test

test:
	lib/tests/test_python.sh
	lib/tests/test_boto.py