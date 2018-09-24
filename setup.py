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

from setuptools import setup

with open('README.md') as f:
    readme = f.read()
    
    
setup(
    name="HADeploy",
    description="An Hadoop Application deployment tool",
    long_description=readme,
    url="https://github.com/BROADSoftware/hadeploy",
    version="0.6.0",
    license="GPLv3",
    author="BROADSoftware",
    author_email="info@hadeploy.com",
    package_dir={ '': 'lib' },
    packages=[ 'hadeploy', 'hadeploy.core', 'hadeploy.plugins' ],
    package_data={
        'hadeploy.core': [ 
            'master/*.*',
            'templates/*.*',
            'conf/*.*'
        ],
        'hadeploy.plugins': [
            '*/*.*',
            '*/*/*.*',
            '*/*/*/*.*',
            '*/*/*/*/*.*'
        ]
    },
    exclude_package_data={ 
        'hadeploy.core': [ 
            'master/*.pyc'
        ],
        'hadeploy.plugins': [ 
            '*/*.pyc',
            '*/*/*.pyc',
            '*/*/*/*.pyc',
            '*/*/*/*/*.pyc'
        ]
    },
    install_requires=[
        'ansible >= 2.3.0.0', 
        'pykwalify >= 1.6.0' 
    ],
    scripts=[ 'bin/hadeploy' ],
    entry_points={
        'console_scripts': ['hadeploy-main=hadeploy.core.main:main']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Software Distribution',
        'Topic :: Utilities',
    ],
    keywords='hadoop deployement bigdata big-data hdfs hbase hive kafka ranger'  
)

