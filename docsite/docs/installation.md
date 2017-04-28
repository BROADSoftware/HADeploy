#Installation

##Prerequisite

HADeploy node must be a Linux system.

Current installation process has been tested on RHEL/CentOS7 (Python 2.7). Installation on other Linux Variant may works. All feedbacks are welcome.

##Installation from GIT repository

This is currently the only installation method available.

First, install several required package:

```bash
sudo yum install -y git python-pip python-devel libffi-devel openssl-devel
```

Then clone the HADeploy git repository:

```bash
git clone https://github.com/BROADSoftware/hadeploy.git
```

Move to the newly create directory: 

```bash
cd hadeploy
```

Switch on a stable version.

```bash
git checkout v0.X.X
```

(Use git tag to have a list of all versions. See ROADMAP.md for the latest stable)

And perform required python module installation using pip:

```bash
sudo pip install -r requirements.txt
sudo pip install cryptography
```

To perform some Hive, Kafka and HBase configuration, HADeploy will use some specific modules. These need to be downloaded to complete the installation. For this:

```bash
cd helper
chmod +x build.sh
./build.sh
```

And, last but not least, add HADeploy to your path:

```bash
cd ../bin
export PATH=$PATH:$(pwd)
# or
export PATH=$PATH:<whereHADeployWasCloned>/hadeploy/bin
```

You are now ready to used HADeploy from this workstation.



