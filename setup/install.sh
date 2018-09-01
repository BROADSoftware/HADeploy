#!/bin/bash

NAME=virtualenv

MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

virtualenv ${MYDIR}/../${NAME}

source ${MYDIR}/../${NAME}/bin/activate

#pip install --upgrade pip
curl https://bootstrap.pypa.io/get-pip.py | python

pip install -r ${MYDIR}/requirements.txt

#bash
deactivate
