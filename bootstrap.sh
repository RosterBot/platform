#!/bin/bash

echo 'Building Virtualenv...'
/usr/bin/env tar xvzf lib/contrib/virtualenv-1.11.tar.gz -C lib/contrib/
/usr/bin/env python lib/contrib/virtualenv-1.11/virtualenv.py .env
source .env/bin/activate
pip install boto
pip install ansible
pip install python_vagrant