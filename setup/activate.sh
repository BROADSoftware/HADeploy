#!/bin/bash

NAME=virtualenv

MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source ${MYDIR}/../${NAME}/bin/activate

PATH=$PATH:${MYDIR}/../bin

PS1='[hadeploy] \h:\W \u\$ '
