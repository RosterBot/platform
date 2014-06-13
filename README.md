platform
========


# Invoke Labs Platform

## Project Mission

##### _A business building company that equips new digital ventures for long term success._

  The mission of this project is to build *a collection of software tools* that allow individual software developers to *build, test, and deploy production ready server software* to an *enterprise level*.

  When we say _a collection of software tools_ we mean that we intend to research the landscape of server deployment and build tools, and select tools that meet our needs. In particular we are guided by the principle that the fewer tools intertwined together, the more robust our system will be. For this reason, we are focusing our effort on the [Ansible](http://www.ansibleworks.com) tool for the overall configuration mechanism.

  When we way _build, test, and deploy_ we mean that we intend to create a system that can provision servers, install frameworks, libraries, or daemon software and verify their correct operation. We further mean that we intend to create a system that can deploy any software application that follows its conventions.

  When we say _production ready server software_  we mean server software that can be relied upon in live production to meet the needs of real users.  That also means that the software should be stable, and that developers can rely on knowing that if the platform works for them locally in development, it will also work for them in production.

  When we say _enterprise level_ we mean that the quality of the system is high, and that it can scale up to many developers just as easily as it can scale up to thousands or millions of users.  We also mean that there will be an emphasis on best practices around security.

## Project Design

#### _Long Term Success_

  In order to meet our mission and equip clients for long term success, we need to focus not only on deploying software, but we also need to understand what software to deploy and how to configure it to meet our objectives. Fundamentally, this is the core aspect of the project. Installing software is easy-- most software comes with an installer and can be installed by the package manager of the system on which it is installed. In order for the system to be effective, we must choose carefully default configurations, and we must provide a way for users of the system to override the defaults where it is useful. Part of our value in this project is to understand which configuration parameters should be overrideable easily and which ones should not be. There is less utility in providing an infinitely configurable system versus providing a system that allows for configurability only where necessary and makes best-practice decisions on behalf of users.

  Furthermore, any individual server resource, even properly configured, only has value when it is used as part of a larger system. In order to provide a platform which businesses can find valuable, we need to provide a system that, when deployed, is more than the sum of its parts, and in order to accomplish that we need to be able to provide a set of software architectural patterns that direct how the parts are to be used together to accomplish the business goals of the software that runs on the platform.

### Sub-Components

#### Ansible Roles

 These are a set of Ansible tasks grouped into roles, using the _roles_ feature of Ansible that was introduced into version 1.2. The purpose of the roles feature is to provide reusable tasks that install and configure software packages according to their use, and not according to the packages themselves. So, for example, it would be appropriate to talk about a *webserver role* rather than an *apache role* or *nginx role*. Whether or not apache or nginx is the web server software used under the hood is less important that having correct configuration of the one chosen.

 We see a further distinction, for example, between a SQL database role and a NoSQL database role, and intend to provide both.

 In Ansible 1.3, a further addition to the _roles_ feature will appear: _role dependencies_.  When ansible 1.3 is released, we will examine this feature and see how it may be incorporated if needed.

 The fundamental goal of the _roles_ in the platform is to help abstract away the implementation details of the parts of the whole-- to encapsulate the webserver or database or logging functionality that every application requires, and thereby to allow a user of the platform to provide an answer to the question "I need some webservers, some SQL database servers, and a message broker server, how do I get that up and running and configured for production?". Our goal is to answer that question with: "You don't-- you describe declaratively what you need, and the system builds it for you."  This is inherently different than many other systems today. There are also systems that do something similar, however our goal is to build a system that is already integrated and helps users to start running applications immediately. Furthermore many of the systems already existing provide only the mildest scaffolding-- the user must specify every detail declaratively. We will take care of this level of detail.

#### Ansible AWS Provisioning

Provisioning is the creation and configuration of the underlying resources on which the aforementioned _roles_ will run. In the case of AWS, provisioning can happen many different ways. We will use the modules provided by Ansible (via the python boto project) to provision AWS instances, combined with AWS CloudFormation JSON documents, to provision AWS resources. The entire AWS provisioning system will consist only of CloudFormation JSON documents and Ansible tasks.

#### Vagrant Local Provisioning

Since the platform will need to build local development environments as well for users, vagrant will be used to provision local resources only. Vagrant will run the same Ansible scripts as used when provisioning in AWS.

#### Glue + Inventory

Invariably we will need to glue these parts together in a straightforward and simple way, including provding a command-line interface and configuration file for users to very simply tell the system what they want. Furthermore, Ansible relies heavily on a concept of inventory and inventory variables to control its behavior. We will need a mechanism for this inventory to be managed as well as for variables to be modified based on how the user requires configuration. The mechanism we will use for that purpose is the python program ```waf```.  That means that the most basic dependency is python+waf.

#### Diagram

![design diagram](https://bitbucket.org/invokelabs/invoke-labs-platform/wiki/Design/design.png "Design")

_Please note that this design is subject to change._

## Directory Structure

	./wscript
	./platform
	./platform.yml
	./lib/
	./lib/roles/
	./lib/tests/
	./lib/vagrant/
	./lib/AWS/
	./lib/ansible/
	./lib/glue/
	./inventory/

### wscript

The wscript file defines the public "interface" into the Platform via waf targets. Users of the system use the targets in the wscript file to do things like:

* Validate their environment.
* Tell the platform to download the application from git.
* Deploy the platform+application into AWS or locally into Vagrant.
* Provision new resources into AWS or locally into Vagrant (e.g. adding a new RDS read-replica or Redis instance).

### platform

The ```platform``` file is the executable copy of the ```waf``` program used to run the platform.

### platform.yml

The configuration file determines how the waf build script carries out its steps, and defines all public parameters available to the user. For example,

* Whether or not a particular kind of role server should be in an AWS auto-scaling group.
* How many of a particular kind of role servers are required (e.g., three webservers, two message brokers).
* What git repository holds the application.
* AWS details, such as which IAM roles should be used for provisioning.
* AWS VPC details, such as what subnets should be created.
* Which git repository hashes of the application correspond to which versions of the application, or if versioning is desired at all.
* Which vagrant box files to use.

### lib/roles

Contains the git submodule pointing to the Ansible roles. The Ansible roles will for the most part follow the existing roles convention, however there may be a desire to put certain behavior into the roles that would otherwise live outside of them in another part of the Platform.

### lib/test

Contains the tests (written in python, except for the python test), that determine whether or the system on which the Platform is being executed meets its requirements. This includes verifying the installation (for version and basic exection of the following tools):

* Ansible
* Python
* python-boto
* Vagrant
* Virtualbox

### lib/vagrant

Contains python scripts for managing+generating Vagrantfiles so that vagrant will correctly provision virtual machines locally according to the Platform specification.

### lib/AWS

Contains python scripts for managing+generating Ansible inventory files and variables for parts of the platform that are running in AWS.

### lib/ansible

Contains python scripts for working with Ansible, for example any custom modules that might be needed or scripts to manage inventory based on Platform configuration that is separate from being specific to AWS.

### lib/glue

Contains python scripts that glue as required any of the rest of the system.

### inventory/

Contains both generated and default inventory files, particularly inventory variables, that are used to determine Ansible's behavior.


_Please note that this directory structure is subject to change_.
