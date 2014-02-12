__author__ = 'invoked'

from vpc import build_vpc_template
import yaml

def generate_vpc_template(task):
    if task.env.platform["Infrastructure"]["VPC"]:
        template = build_vpc_template(task.env.platform["Infrastructure"]["VPC"])
        task.outputs[0].write(template.to_json())


def generate_vpc_playbook(task):
    vpc_stack_play = [
        {
            'hosts': 'localhost',
            'connection': 'local',
            'gather_facts': False,
            'tasks': [
                {
                    'name': 'Booting VPC: ' + task.env.platform["Infrastructure"]["VPC"]["Name"] ,
                    'action': 'cloudformation stack_name='
                          + task.env.platform["Infrastructure"]["VPC"]["Name"] +
                          ' state=present template='
                          + task.inputs[0].abspath() +
                          ' region='
                          + task.env.platform["Infrastructure"]["Region"]
                }
            ]
        }
    ]
    yam = yaml.dump(vpc_stack_play)
    task.outputs[0].write(yam)


def create_management_host(task):
    management_role = [role for role in task.env.platform["Infrastructure"]["Role Types"]
                       if role["Name"] == 'management'][0]
    management_host_play = [
        {
            'hosts': 'localhost',
            'connection': 'local',
            'gather_facts': False,
            'tasks': [
                {
                    'name': 'Creating Management Host Into VPC: ' + task.env.platform["Infrastructure"]["VPC"]["Name"],
                    'local_action': {
                        'module': 'ec2',
                        'id': 'management-' + task.env.platform["Infrastructure"]["VPC"]["Name"],
                        'image': task.env.platform["Infrastructure"]["Default AMI"],
                        'instance_type': management_role["Instance Type"],
                        'key_name': management_role["Key"],
                        'region': task.env.platform["Infrastructure"]["Region"],
                        'wait': True
                    },
                    'register': 'management_ec2'
                }
            ]

        }
    ]
    yam = yaml.dump(management_host_play)
    task.outputs[0].write(yam)



