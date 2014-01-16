#! /usr/bin/env python
# encoding: utf-8

from waflib.Configure import conf


def options(ctx):
    """Configuration step for the platform."""
    ctx.add_option('--skip-local-check', action='store', default=False, help='Skip vagrant and VirtualBox checks.')


def configure(ctx):
    """Configure step for the platform."""
    ctx.check()


def build(ctx):
    """Build step for the platform."""
    pass


@conf
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
        if not ctx.options.skip_local_check:
            vagrant_test.test()
            virtualbox_test.test()
    except Exception as inst:
        print '\033[0;31m'
        print inst
        print '\033[0m'
        exit(1)
