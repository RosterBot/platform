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
                'register': 'vpc'
            }
        ]}
    vpc_stack_play.update(default_local_play)
    yam = yaml.dump([vpc_stack_play])
    task.outputs[0].write(yam)


def create_management_host(task):
    management_role = [role for role in task.env.platform["Infrastructure"]["Role Types"]
                       if role["Name"] == 'management'][0]

    tasks = list()
    for i in range(management_role["Instance Count"]):
        tasks.append({
            'name': 'Creating Management Host Into VPC: ' + task.env.platform["Infrastructure"]["VPC"]["Name"],
            'action': {
                'module': 'ec2',
                'id': 'management-' + task.env.platform["Infrastructure"]["VPC"]["Name"] + "-" + str(i),
                'image': task.env.platform["Infrastructure"]["Default AMI"],
                'instance_type': management_role["Instance Type"],
                'key_name': management_role["Key"],
                'region': task.env.platform["Infrastructure"]["Region"],
                'instance_tags': {"Role": management_role["Name"], "Name": management_role["Name"] + str(i)},
                'wait': True,
                'group_id': ['{{ vpc.stack_outputs.SSHFromAnywhere }}', '{{ vpc.stack_outputs.defaultSG }}'],
                'vpc_subnet_id': '{{ vpc.stack_outputs.management2 }}',
                'assign_public_ip': True  # this is sort of a temporary hack I presume.
            },
            'register': 'management_ec2_' + str(i)
        })
        # tasks.append({
        #     'name': 'Create an EIP for Management host.',
        #     'action': {
        #         'module': 'ec2_eip',
        #         'in_vpc': True,
        #         'instance_id': '{{  management_ec2_' + str(i) + '.instance_ids[0] }}',
        #         'region': task.env.platform["Infrastructure"]["Region"]
        #     }
        # })

    management_host_play = {
        'tasks': tasks
    }
    management_host_play.update(default_local_play)
    yam = yaml.dump([management_host_play])
    task.outputs[0].write(yam)





