
# Juniper Networks vMX lwaftr Docker Container

The vmx-docker-lwaftr Docker Container contains everything thats required to successfully launch vMX 16.1R3 and newer images with a configuration file and license key. This document describes how that Container can be built from source. The actual vMX images is NOT part of the Container. It will be loaded from the official vMX tar file placed in the local directory from where the Container is launched.

Consult the Juniper White Paper on [vMX Lightweight 4over6 Virtual Network Function](https://www.juniper.net/assets/us/en/local/pdf/whitepapers/2000648-en.pdf) for a solution overview and listen to the podcast on Software Gone Wild by Ivan Pepelnjak, Dec 2016: [Blog](http://blog.ipspace.net/2016/12/snabb-switch-with-vmx-control-plane-on.html), [MP3](http://stream.ipspace.net/nuggets/podcast/Show_68-lwAFTR_Snabb_Data_Plane_with_vMX_Control_Plane.mp3).

## Build instructions

The Container vmx-docker-lwaftr is based on the official Ubuntu Docker 14.04.5 base Container and includes the following elements:

* Qemu 
* Snabb
* JET Python Client Library

Clone the repo with submodules:

```
git clone https://github.com/Juniper/vmx-docker-lwaftr
```

Or to clone a specific version by tag, use git option '-b' to specify a specific tag:

```
git clone -b v1.2.0 https://github.com/juniper/vmx-docker-lwaftr
```

A single top level execution of make will build the containers for vmx-docker-lwaftr and packetblaster. Check the Makefile on how to use docker-compose build directly.

```
make
```

```
$ docker images |head
REPOSITORY                           TAG                 IMAGE ID            CREATED             SIZE
vmxdockerlwaftr_packetblaster        latest              2779cc4e2b4e        9 minutes ago       8.24MB
vmxdockerlwaftr_lwaftr               latest              407b7c3f1128        25 minutes ago      525MB...
vmxdockerlwaftr_b4cpe                latest              b24271e3fd10        3 seconds ago       260MB
```

The image build be removed via 'make clean' from the qemu, respectively snabb directory. Only the 'vmx-docker-lwaftr' Container is required.

### 5. Save vmx-docker-lwaftr Container to file

To save the vmx-docker-lwaftr Container into an image file use:

```
$ docker save -o vmx-docker-lwaftr-v1.2.0.img vmx-docker-lwaftr:v1.2.0
$ ls -l vmx-docker-lwaftr-v1.2.0.img
-rw------- 1 mwiget staff 262911488 Sep  11 21:40 vmx-docker-lwaftr-v1.2.0.img
```

## Running the vmx-docker-lwaftr Container

```
docker run --name <name> --rm -v \$PWD:/u:ro \\
   --privileged -i -t marcelwiget/vmx-docker-lwaftr[:version] \\
   -c <junos_config_file> -I identity [-l license_file]\\
   [-V <# of cores>] [-W <# of cores>] [-P <cores>] [-R <cores>] \\
   [-m <kbytes>] [-M <kBytes>] \\
   <image> <pci-address/core> [<pci-address/core> ...]

[:version]       Container version. Defaults to :latest

 -v \$PWD:/u:ro   Required to access a file in the current directory
                 docker is executed from (ro forces read-only access)
                 The file will be copied from this location

 <image>         vMX distribution tar file, e.g. vmx-bundle-16.1R3.10.tgz

 <pci-address/core> [<pci-address/core> ..]
                 One or more PCI addresses and physical core to lock
                 the Snabb process to. For simulation purposes use
                 'tap' instead of the pci-address. 

 -I  username,password for the JETapp to communicate with the Junos
     control plane or ssh private key file. Must also be configured in 
     the Junos config with super-user privileges

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
