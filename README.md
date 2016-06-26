
# Juniper Networks vMX lwaftr Docker Container

The vmxlwaftr Docker Container contains everything thats required to successfully launch vMX 16.1 and newer images with a configuration file and license key. This document describes how that container can be built from source. The actual vMX images is NOT part of the Container. It will be loaded from the official vMX tar file placed in the local directory from where the Container is launched.

## Build instructions

The Container vmxlwaftr is based on the official Ubuntu Docker 14.04.4 base container and includes the following elements:

* Qemu 2.4.1 with reconnect patch downloaded and built from source in qemu/
* Snabb, downloaded and built from source in snabb/
* JET toolkit 16.1 (jet-1.tar.gz)
* JET application in the directory jetapp/

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

This will clone branch v2.4.1-snabb from a private qemu repository, build the Docker container *buildqemu* to compile and create a binary tar file for qemu into the current directory, from where it will be copied during the final step into the toplevel build directory by the top level Makefile.
In case the qemu must be cloned from a public qemu repository, its imperative to apply the patch qemu/qemu-snabb.diff to allow Snabb to re-connect to the VhostUser Socket after it terminated. The patch works also on v2.5.0 but needs adjustements for v2.6.0

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

This will clone the branch 1to1_mapping from a private Snabb repository, build the Docker container *buildsnabb* to compile snabb and place it in the current directory. Snabb is a single application that will be placed in /usr/local/bin/ in the vmxlwaftr Docker Container further below.

### 3. Download JET Toolkit

The toplevel Makefile will automatically download the jet-1.tar.gz from Juniper's internal /volume/build/ folder for 16.1. This is a temporary solution until the toolkit can be downloaded from an external/public repository.

For a manual download, use:

```
scp svpod1-vmm.englab.juniper.net:/volume/build/junos/16.1/release/16.1R1.6/ship/jet-1.tar.gz .
```

### 4. Build the vmxlwaftr container

Edit the name and version of the container in the toplevel file VERSION:

```
$ cat VERSION
vmxlwaftr:v0.9
```

If the container is to be pushed onto docker hub, then the name will probably be something like *juniper/vmxlwaftr:vx.y*

Run the toplevel Makefile to build the container:

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

The images buildsnabb and buildqemu can be removed via 'make clean' from the qemu, respectively snabb directory. Only the 'vmxlwaftr' container is required.

### 5. Save vmxlwaftr Container to file

To save the vmxlwaftr container into an image file use:

```
$ docker save -o vmxlwaftr-v0.9.img vmxlwaftr:v0.9
$ ls -l vmxlwaftr-v0.9.img
-rw------- 1 mwiget mwiget 447854592 Jun 26 18:54 vmxlwaftr-v0.9.img
```

## Running the vmxlwaftr Container

```
docker run --name <name> --rm -v \$PWD:/u:ro \\
   --privileged -i -t marcelwiget/vmxlwaftr[:version] \\
   -c <junos_config_file> -i identity [-l license_file] \\
   [-m <kbytes>] [-M <kBytes>] [-V <cores>] [-W <cores>] \\
   <image> <pci-address/core> [<pci-address/core> ...]

[:version]       Container version. Defaults to :latest

 -v \$PWD:/u:ro   Required to access a file in the current directory
                 docker is executed from (ro forces read-only access)
                 The file will be copied from this location

 -l  license_file to be loaded at startup (requires user snabbvmx with ssh
     private key given via option -i)

 -i  ssh private key for user snabbvmx 
     (required to access lwaftr config via netconf)

 -m  Specify the amount of memory for the vRE/VCP (default $VCPMEM kB)
 -M  Specify the amount of memory for the vPFE/VFP (default $VFPMEM kB)

 -V  number of vCPU's to assign to the vRE/VCP (default $VCPCPU)
 -W  number of vCPU's to assign to vPFE/VFP (default $VFPCPU)

 -d  launch debug shell before launching vMX

 -X  cpu list for vPFE and vRE

<pci-address/core>  PCI Address of the Intel 825999 based 10GE port with core to pin snabb on.  Multiple ports can be specified, space separated
```

Example:

```
docker run --name lwaftr1 --rm --privileged -v \$PWD:/u:ro \\
  -i -t marcelwiget/vmxlwaftr -c lwaftr1.txt -i snabbvmx.key \\
  jinstall64-vrr-14.2R5.8-domestic.img 0000:05:00.0/7 0000:05:00.0/8
```

