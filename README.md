
# Juniper Networks vMX lwaftr Docker Container

The vmxlwaftr Docker Container contains everything thats required to successfully launch vMX 16.1 and newer images with a configuration file and license key. This document describes how that Container can be built from source. The actual vMX images is NOT part of the Container. It will be loaded from the official vMX tar file placed in the local directory from where the Container is launched.

## Build instructions

The Container vmxlwaftr is based on the official Ubuntu Docker 14.04.4 base Container and includes the following elements:

* Qemu 2.4.1 with reconnect patch downloaded and built from source in qemu/
* Snabb, downloaded and built from source in snabb/

The build process requires a Docker Engine, ideally on a Linux based host. It is however possible to build it entirely on Docker for OS/X.

The individual steps are:

### 1. Build qemu

```
$ cd qemu
$ make
$ ls qemu-*tgz
qemu-v2.4.1-snabb.tgz
cd ..
```

This will clone a tagged release version from the official github qemu repository, apply the required reconnect patch and build the Docker Container *buildqemu* to compile and create a binary tar file for qemu into the current directory, from where it will be copied during the final step into the toplevel build directory by the top level Makefile.
The patch qemu/qemu-snabb.diff allows Snabb to re-connect to the VhostUser Socket after it terminated. The patch will needs adjustements to work with v2.6.0 and newer versions of qemu. While the patch works with v2.5.1.1, the vPFE image became unstable (show chassis fpc reporting 'unresponsive').

### 2. Build Snabb

```
$ cd snabb
$ make
. . .
make[1]: Leaving directory `/build/src'
c18e43a1bbc434860275618d446c1eef  src/snabb
c18e43a1bbc434860275618d446c1eef  /u/src/snabb
cp build/src/snabb .
$ md5sum snabb
c18e43a1bbc434860275618d446c1eef  snabb
$ cd ..
```

This will clone the branch 1to1_mapping from a private Snabb repository, build the Docker Container *buildsnabb* to compile snabb and place it in the current directory. Snabb is a single application that will be placed in /usr/local/bin/ in the vmxlwaftr Docker Container further below.

### 3. JET

Download the following files from the Internet. They will be installed into the Container by step 4.

```
wget https://pypi.python.org/packages/82/d9/7064d3a0a1d62756a1a809c85b99f864c641b66de84c15458f72193b7708/paho-mqtt-1.2.tar.gz
wget https://pypi.python.org/packages/ae/58/35e3f0cd290039ff862c2c9d8ae8a76896665d70343d833bdc2f748b8e55/thrift-0.9.3.tar.gz
wget https://bootstrap.pypa.io/ez_setup.py
```

Download jet-1.tar.gz from the juniper.net support download page for JET:
http://www.juniper.net/support/downloads/?p=jet#sw

### 4. Build the vmxlwaftr Container

Edit the name and version of the Container in the toplevel file VERSION:

```
$ cat VERSION
vmxlwaftr:v0.9
```

If the Container is to be pushed onto docker hub, then the name will probably be something like *juniper/vmxlwaftr:vx.y*

Run the toplevel Makefile to build the Container:

```
$ make
. . .
Step 15 : CMD -h
 ---> Running in f98dc81620c9
 ---> aa7e281472e4
Removing intermediate container f98dc81620c9
Successfully built aa7e281472e4

$ mwiget@st:~/vmxlwaftr$ docker images
REPOSITORY                       TAG                 IMAGE ID            CREATED             SIZE
vmxlwaftr                        v0.9                aa7e281472e4        13 minutes ago      431.4 MB
buildsnabb                       latest              d633187d8dfc        29 minutes ago      358.8 MB
buildqemu                        latest              5c8eace386ab        35 minutes ago      447.2 MB
. . .
```

The images buildsnabb and buildqemu can be removed via 'make clean' from the qemu, respectively snabb directory. Only the 'vmxlwaftr' Container is required.

### 5. Save vmxlwaftr Container to file

To save the vmxlwaftr Container into an image file use:

```
$ docker save -o vmxlwaftr-v0.9.img vmxlwaftr:v0.9
$ ls -l vmxlwaftr-v0.9.img
-rw------- 1 mwiget mwiget 447854592 Jun 26 18:54 vmxlwaftr-v0.9.img
```

## Running the vmxlwaftr Container

```
docker run --name <name> --rm -v \$PWD:/u:ro \\
   --privileged -i -t marcelwiget/vmxlwaftr[:version] \\
   -c <junos_config_file> -i identity [-l license_file]\\
   [-V <# of cores>] [-W <# of cores>] [-P <cores>] [-R <cores>] \\
   [-m <kbytes>] [-M <kBytes>] \\
   <image> <pci-address/core> [<pci-address/core> ...]

[:version]       Container version. Defaults to :latest

 -v \$PWD:/u:ro   Required to access a file in the current directory
                 docker is executed from (ro forces read-only access)
                 The file will be copied from this location

 <image>         vMX distribution tar file, e.g. vmx-bundle-16.1R1.6.tgz

 <pci-address/core> [<pci-address/core> ..]
                 One or more PCI addresses and physical core to lock
                 the Snabb process to. For simulation purposes use
                 'tap' instead of the pci-address. 

 -i  username,password for the JETapp to communicate with the Junos
     control plane. Must also be configured in the Junos config with
     super-user privileges

 -c  Junos configuration file

 -l  Junos license key file

 -m  Specify the amount of memory for the vRE/VCP (default $VCPMEM kB)
 -M  Specify the amount of memory for the vPFE/VFP (default $VFPMEM kB)

 -P  Cores to pin the VFP to via numactl --physcpubind <cores>
 -R  Cores to pin the VCP to via numactl --physcpubind <cores>
 
 -V  number of virtual cores to assign to VCP (default 1)
 -W  number of virtual cores to assign to VFP (default 3)

 -d  launch debug shell before launching vMX and before existing the container

```

See tests/run1.sh and tests/run2.sh for examples on how to launch. The 
vMX distribution tar file must be on the local directory from which the container
is launched.

