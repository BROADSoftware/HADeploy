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

JDCTOPIC_VERSION="0.2.0"

if [ ! -f $MYDIR/jdctopic/jdctopic_uber-${JDCTOPIC_VERSION}.jar ]
then
	echo 
	echo "******************** Will download jdctopic_uber-${JDCTOPIC_VERSION}.jar"
	echo 
	curl -L https://github.com/Kappaware/jdctopic/releases/download/v${JDCTOPIC_VERSION}/jdctopic_uber-${JDCTOPIC_VERSION}.jar -o $MYDIR/jdctopic/jdctopic_uber-${JDCTOPIC_VERSION}.jar
else
	echo "-------------------- jdctopic_uber-${JDCTOPIC_VERSION}.jar already downloaded"
fi



