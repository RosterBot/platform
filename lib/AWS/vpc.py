__author__ = 'invoked'

from troposphere import Ref, Template
import troposphere.ec2 as ec2
import netaddr

## basic idea / algo
## create the system in multiple passes
## first, launch the most basic VPC
## with any subnets
## if a nat instance is desired, launch that.
## then create private subnet route tables using the nat instance's network interface


def build_vpc_step1():
    print "step1"


def build_vpc_template(vpc_config):
    vpc = ec2.VPC(name=vpc_config["Name"], CidrBlock=vpc_config["IP Range"])
    vpc.Tags = [{"Key": "Application", "Value": Ref("AWS::StackId")}]
    vpc_config["Subnets"].sort(key=lambda net: net["IP Count"], reverse=True)
    subnets = build_subnets(vpc_config["Subnets"], vpc_config["IP Range"], vpc_config["Name"])
    [subnet.Tags.append(vpc.Tags[0]) for subnet in subnets]
    t = Template()
    t.add_resource(vpc)
    [t.add_resource(subnet) for subnet in subnets]
    print(t.to_json())


def calculate_cidr_prefix(num_of_ips):
    # brute force method for determining prefix
    # taken from zytrax.org
    p = 1
    n = int(num_of_ips)
    i = 0
    while p < n:
        p *= 2
        i += 1
    prefix = 32 - i
    return prefix


def build_subnets(subnets, ip_range, vpc):
    network = netaddr.IPNetwork(ip_range)
    chosen_nets = []

    def create_vpc_subnet(subnet):
        prefix = calculate_cidr_prefix(subnet[1]["IP Count"])
        possible_nets = list(network.subnet(prefix))
        if subnet[0] == 0:
            cidrblock = possible_nets[0]
            chosen_nets.append(possible_nets[0])
        else:
            net = None
            for chosen_net in chosen_nets:
                for possible_net in possible_nets:
                    if possible_net in chosen_net:
                        continue
                    else:
                        net = possible_net
            chosen_nets.append(net)
            cidrblock = net
        tags = [{"Key": "Network", "Value": subnet[1]["Type"]}]
        return ec2.Subnet(name=subnet[1]["Name"], CidrBlock=str(cidrblock), VpcId=Ref(vpc), Tags=tags)

    return map(create_vpc_subnet, list(enumerate(subnets)))

def build_private_route_table(vpc):
    private_table = ec2.RouteTable(name="Private Table")
    private_table.Tags = [{"Key": "Network", "Value": "Private"}, {"Key": "Application", "Value": Ref("AWS::StackId")}]
    private_table.VpcId = Ref(vpc)
    return private_table