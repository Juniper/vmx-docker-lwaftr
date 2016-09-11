
# Juniper Networks vMX lwaftr Docker Container

The vmxlwaftr Docker Container contains everything thats required to successfully launch vMX 16.1 and newer images with a configuration file and license key. This document describes how that Container can be built from source. The actual vMX images is NOT part of the Container. It will be loaded from the official vMX tar file placed in the local directory from where the Container is launched.

## Build instructions

The Container vmxlwaftr is based on the official Ubuntu Docker 14.04.4 base Container and includes the following elements:

* Qemu 2.4.1 with reconnect patch downloaded and built from source in qemu/
* Snabb, downloaded and built from source in snabb/

The build process requires a Docker Engine and the make tool. Please follow the official 
[Install Docker Engine on Linux](https://docs.docker.com/engine/installation/linux/) guide. Docker engine 1.12.1 
or newer is required to run the lwaftr1 simulation in the tests directory. 

A single top level execution of make will build Snabb, Qemu and, dumb-init with temporary build containers and create the vmxlwaftr Docker container.

```
make
```

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

This will clone the branch lwaftr from github.com/igalia, build the Docker Container *buildsnabb* to compile snabb and place it in the current directory. Snabb is a single application that will be placed in /usr/local/bin/ in the vmxlwaftr Docker Container further below.

### 4. dumb-init

dumb-init is a simple process supervisor and init system designed to run as PID 1 inside minimal container environments (such as Docker). It is a deployed as a small, statically-linked binary written in C. It clones version 1.1.3 from https://github.com/Yelp/dumb-init and builds it via Docker container.


```
$ cd dumb-init
$ make
...
```

### 5. Build the vmxlwaftr Container

Edit the name and version of the Container in the toplevel file VERSION:

```
$ cat VERSION
vmxlwaftr:v0.11
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
REPOSITORY              TAG                 IMAGE ID            CREATED              SIZE
vmxlwaftr               v0.11               2779b5c29172        About a minute ago   253.2 MB
buildqemu               latest              dfcbe71b7896        2 minutes ago        432.5 MB
buildsnabb              latest              60f090d9d3e0        4 minutes ago        344.7 MB
build-dumb-init         latest              866eb14689e5        6 minutes ago        347.8 MB
b4cpe                   v0.1                fb4f557e6249        3 days ago           258.6 MB
ubuntu                  14.04.4             38c759202e30        10 weeks ago         196.6 MB
...
```

The images buildsnabb and buildqemu can be removed via 'make clean' from the qemu, respectively snabb directory. Only the 'vmxlwaftr' Container is required.

### 5. Save vmxlwaftr Container to file

To save the vmxlwaftr Container into an image file use:

```
$ docker save -o vmxlwaftr-v0.11.img vmxlwaftr:v0.11
$ ls -l vmxlwaftr-v0.11.img
-rw------- 1 mwiget staff 262911488 Sep  11 21:40 vmxlwaftr-v0.11.img
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

See tests/run0.sh, tests/run1.sh and tests/run2.sh for examples on how to launch. The 
vMX distribution tar file must be on the local directory from which the container
is launched.

