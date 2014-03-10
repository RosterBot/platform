__author__ = 'invoked'

from vpc import build_vpc_template
import yaml

default_local_play = {
    'hosts': 'localhost',
    'connection': 'local',
    'gather_facts': False
}


def generate_vpc_template(task):
    if task.env.platform["Infrastructure"]["VPC"]:
        template = build_vpc_template(task.env.platform["Infrastructure"]["VPC"])
        task.outputs[0].write(template.to_json())


def generate_vpc_playbook(task):
    vpc_stack_play = {
        'tasks': [
            {
                'name': 'Booting VPC: ' + task.env.platform["Infrastructure"]["VPC"]["Name"],
                'action': 'cloudformation stack_name='
                        + task.env.platform["Infrastructure"]["VPC"]["Name"] +
                        ' state=present template='
                        + task.inputs[0].abspath() +
                        ' region='
                        + task.env.platform["Infrastructure"]["Region"],
                'register': 'vpc',
                'ignore_errors': True
            }
        ]}
    vpc_stack_play.update(default_local_play)
    yam = yaml.dump([vpc_stack_play])
    task.outputs[0].write(yam)


def _create_management_hosts(management_role, task, vpc_name):
    tasks = list()
    for i in range(management_role["Instance Count"]):
        tasks.append({
            'name': 'Creating Management Host Into VPC: ' + vpc_name,
            'action': {
                'module': 'ec2',
                'id': vpc_name + '-management-' + str(i),
                'image': task.env.platform["Infrastructure"]["Default AMI"],
                'instance_type': management_role["Instance Type"],
                'key_name': management_role["Key"],
                'region': task.env.platform["Infrastructure"]["Region"],
                'instance_tags': {
                    "Role": vpc_name + '_' + management_role["Name"],
                    "Name": vpc_name + '_' + management_role["Name"] + str(i)
                },
                'wait': True,
                'group_id': ['{{ vpc.stack_outputs.SSHFromAnywhere }}', '{{ vpc.stack_outputs.defaultSG }}'],
                'vpc_subnet_id': '{{ vpc.stack_outputs.'
                                 + [management_subnet["Name"]
                                    for management_subnet in task.env.platform["Infrastructure"]["VPC"]["Subnets"]
                                    if management_subnet["Role Type"] == "management"][0] +
                                 ' }}',
                'assign_public_ip': True  # this is sort of a temporary hack I presume.
            },
            'register': 'management_ec2_' + str(i),
            'when': 'vpc.stack_outputs is defined'
        })
        tasks.append({
            'name': 'Add management hosts to inventory.',
            'action': {
                'module': 'add_host',
                'hostname': '{{ item.public_ip }}',
                'groupname': management_role["Name"]
            },
            'with_items': 'management_ec2_' + str(i) + '.instances',
            'when': 'management_ec2_' + str(i) + '.instances is defined'
        })
        tasks.append({
            'name': 'Sleep until SSH is available.',
            'action': {
                'module': 'wait_for',
                'host': '{{ item.public_ip }}',
                'port': '22',
                'state': 'started'
            },
            'with_items': 'management_ec2_' + str(i) + '.instances',
            'when': 'management_ec2_' + str(i) + '.instances is defined'
        })
    return tasks


def generate_management_host_playbook(task):
    management_roles = [role for role in task.env.platform["Infrastructure"]["Role Types"]
                        if role["Name"] == 'management']

    if len(management_roles) != 1:
        raise RuntimeError('You may only specify a single management role type.')

    management_role = management_roles[0]
    vpc_name = task.env.platform["Infrastructure"]["VPC"]["Name"]

    tasks = _create_management_hosts(management_role, task, vpc_name)

    apply_management_role_play = {
        'name': 'Apply management role to management hosts.',
        'hosts': ['tag_Role_' + vpc_name + '_' + management_role["Name"], management_role["Name"]],
        'gather_facts': True,
        'sudo': True,
        'user': 'ubuntu',
        'roles': ['../../lib/roles/common']
    }

    management_host_play = {
        'tasks': tasks
    }
    management_host_play.update(default_local_play)
    yam = yaml.dump([management_host_play, apply_management_role_play])
    task.outputs[0].write(yam)
