import util

def executable_test():
	import vagrant
	import os
	import subprocess
	import re
	command = vagrant.which("VBoxManage"), "--version"
	current_version = re.search('(\d+\.[^r]*)', subprocess.check_output(command, cwd=os.getcwd())).group(0)
	minimum_version = "4.2.18"
	util.compare_versions(minimum_version, current_version, "VBoxManage binary")

def test():
	executable_test()