#!/usr/bin/env bash
#
# Copyright (C) 2017 BROADSoftware
#
# This file is part of HADeploy
#
# HADeploy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HADeploy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HADeploy.  If not, see <http://www.gnu.org/licenses/>.

MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

JDCHTABLE_VERSION="0.2.0"
HBLOAD_VERSION="0.2.0"

if [ ! -f $MYDIR/jdchtable/jdchtable_uber-${JDCHTABLE_VERSION}.jar ]
then
	echo 
	echo "******************** Will download jdchtable_uber-${JDCHTABLE_VERSION}.jar"
	echo 
	curl -L https://github.com/BROADSoftware/jdchtable/releases/download/v${JDCHTABLE_VERSION}/jdchtable_uber-${JDCHTABLE_VERSION}.jar -o $MYDIR/jdchtable/jdchtable_uber-${JDCHTABLE_VERSION}.jar
else 
	echo "-------------------- jdchtable_uber-${JDCHTABLE_VERSION}.jar already downloaded"
fi

if [ ! -f $MYDIR/hbload/hbload_uber-${HBLOAD_VERSION}.jar ]
then
	echo
	echo "******************** Will download hbload_uber-${HBLOAD_VERSION}.jar"
	echo 
	curl -L https://github.com/BROADSoftware/hbtools/releases/download/v${HBLOAD_VERSION}/hbload_uber-${HBLOAD_VERSION}.jar -o $MYDIR/hbload/hbload_uber-${HBLOAD_VERSION}.jar
else 
	echo "-------------------- hbload_uber-${HBLOAD_VERSION}.jar already downloaded"
fi

