#!/bin/bash

echo 'Building Virtualenv...'
/usr/bin/env tar xvzf lib/contrib/virtualenv-1.11.tar.gz -C lib/contrib/
/usr/bin/env python lib/contrib/virtualenv-1.11/virtualenv.py .env
source .env/bin/activate
pip install boto
pip install ansible
pip install python_vagrant
pip install awscli
pip install netaddr
pip install troposphere
echo "Now run \"source .env/bin/activate\""
echo "To verify dependencies, run \"./platform check\" or  \"./platform check --skip-local-check=true\" if you want to skip the vagrant and virtualbox checks."
echo "You can use \"./platform --help\" to see all options."
