__author__ = 'invoked'

from troposphere import Ref, Template, Output
import troposphere.ec2 as ec2
import netaddr

## basic idea / algo
## create the system in multiple passes
## first, launch the most basic VPC
## with any subnets
## if a nat instance is desired, launch that.
## then create private subnet route tables using the nat instance's network interface


def build_vpc_template(vpc_config):
    vpc_tags = [{"Key": "Application", "Value": Ref("AWS::StackId")}]
    vpc = ec2.VPC(name=vpc_config["Name"],
                  CidrBlock=vpc_config["IP Range"],
                  Tags=vpc_tags)

    vpc_config["Subnets"].sort(key=lambda net: net["IP Count"], reverse=True)

    subnets = build_subnets(vpc_config["Subnets"], vpc_config["IP Range"], vpc_config["Name"])
    private_route_table = build_private_route_table(vpc_config["Name"])
    public_route_table = build_public_route_table(vpc_config["Name"])

    [subnet.Tags.append(vpc.Tags[0]) for subnet in subnets]
    t = Template()
    t.add_resource(vpc)
    t.add_resource(private_route_table)
    t.add_resource(public_route_table)
    [t.add_resource(subnet) for subnet in subnets]
    [t.add_resource(gateway_attachments) for gateway_attachments in build_public_gateway(vpc_config["Name"])]
    management_group = build_management_security_group(vpc_config["Name"])
    t.add_resource(management_group[0])
    t.add_output(management_group[1])

    default_group = build_default_security_group(vpc_config["Name"])
    t.add_resource(default_group[0])
    t.add_resource(default_group[1])
    t.add_output(default_group[2])

    t.add_output(Output(name="vpcId", Value=Ref(vpc_config["Name"])))
    [t.add_output(Output(name=subnet.name, Value=Ref(subnet.name))) for subnet in subnets]
    [t.add_resource(public_route_table_association)
     for public_route_table_association in build_public_route_table_associations(vpc_config["Subnets"])]
    return t


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
            for possible_net in possible_nets:
                ok = True
                for chosen_net in chosen_nets:
                    if possible_net in chosen_net:
                        ok = False
                if ok:
                    net = possible_net
                    break

            if net is None:
                raise ValueError('Unable to fit all subnets in your VPC.')
            chosen_nets.append(net)
            cidrblock = net
        tags = [{"Key": "Network", "Value": subnet[1]["Type"]}]
        return ec2.Subnet(name=subnet[1]["Name"], CidrBlock=str(cidrblock), VpcId=Ref(vpc), Tags=tags)

    return map(create_vpc_subnet, list(enumerate(subnets)))


def build_private_route_table(vpc):
    private_table = ec2.RouteTable(name="PrivateRouteTable")
    private_table.Tags = [{"Key": "Network", "Value": "Private"}, {"Key": "Application", "Value": Ref("AWS::StackId")}]
    private_table.VpcId = Ref(vpc)
    return private_table


def build_public_route_table(vpc):
    public_table = ec2.RouteTable(name="PublicRouteTable")
    public_table.Tags = [{"Key": "Network", "Value": "Public"}, {"Key": "Application", "Value": Ref("AWS::StackId")}]
    public_table.VpcId = Ref(vpc)
    return public_table


def build_public_route(vpc):
    public_route = ec2.Route(name="PublicRoute",
                             RouteTableId=Ref("PublicRouteTable"),
                             DestinationCidrBlock="0.0.0.0/0",
                             GatewayId=Ref("InternetGateway")
                             )
    return public_route


def build_public_route_table_associations(public_subnets):
    public_route_tabl_associations = [ec2.SubnetRouteTableAssociation(name=public_subnet["Name"]
                                                                      + "PublicRouteTableAssociation",
                                                                      SubnetId=Ref(public_subnet["Name"]),
                                                                      RouteTableId=Ref("PublicRouteTable"))
                                      for public_subnet in public_subnets if public_subnet["Type"] is "Public"]
    return public_route_tabl_associations



def build_public_gateway(vpc):
    public_gateway = ec2.InternetGateway(name="InternetGateway",
                                         Tags=[{"Key": "Application", "Value": Ref("AWS::StackId")}])
    attachment = ec2.VPCGatewayAttachment(name="AttachInternetGateway",
                                          VpcId=Ref(vpc),
                                          InternetGatewayId=Ref(public_gateway))
    return [attachment, public_gateway]


def build_management_security_group(vpc):
    egress = [{'CidrIp': '0.0.0.0/0', 'IpProtocol': 'tcp', 'FromPort': '1024', 'ToPort': '65535'}]
    ingress = [{"CidrIp": "0.0.0.0/0", "IpProtocol": "tcp", "FromPort": "22", "ToPort": "22"}]
    group = ec2.SecurityGroup(name='SSHFromAnywhere',
                              VpcId=Ref(vpc),
                              GroupDescription='management group allows ssh from anywhere',
                              SecurityGroupEgress=egress,
                              SecurityGroupIngress=ingress)
    output = Output(name="SSHFromAnywhere", Value=Ref('SSHFromAnywhere'))
    return [group, output]


def build_default_security_group(vpc):
    egress = [{'CidrIp': '0.0.0.0/0', 'IpProtocol': '-1', 'FromPort': '0', 'ToPort': '65535'}]
    group = ec2.SecurityGroup(name='defaultSG',
                              VpcId=Ref(vpc),
                              GroupDescription='default group which allows outbound to anywhere and inbound from within',
                              SecurityGroupEgress=egress,
                              )
    ingress = ec2.SecurityGroupIngress(name="defaultSGingress",
                                       GroupId=Ref("defaultSG"),
                                       IpProtocol='-1',
                                       FromPort="0",
                                       ToPort="65535",
                                       SourceSecurityGroupId=Ref("defaultSG"))
    output = Output(name="defaultSG", Value=Ref('defaultSG'))
    return [group, ingress, output]