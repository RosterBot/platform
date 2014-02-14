#! /usr/bin/env python
# encoding: utf-8

from waflib.Configure import conf
import yaml
from lib import AWS
from lib import glue


APPNAME = 'Platform'
VERSION = '0.0.1'


def generate_final_playbook(task):
    task.outputs[0].write("\n\n".join([file(play.abspath()).read() for play in task.inputs]))


def options(ctx):
    """Configuration step for the platform."""
    ctx.add_option('--skip-local-check', action='store', default=False, help='Skip vagrant and VirtualBox checks.')


def configure(ctx):
    """Configure step for the platform."""
    ctx.env.platform = yaml.load(open('platform.yml'))


def build(ctx):
    """Build step for the platform."""
    ctx(rule=AWS.generate_vpc_template, source='platform.yml', target='vpc_template.json')
    ctx(rule=AWS.generate_vpc_playbook, source='vpc_template.json', target='vpc.playbook')
    ctx(rule=AWS.create_management_host_playbook, source='vpc.playbook', target='management.playbook')
    ctx(rule=generate_final_playbook, source=['vpc.playbook', 'management.playbook'], target='platform.playbook')
    ctx(rule=glue.run_ansible, source='platform.playbook')


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
