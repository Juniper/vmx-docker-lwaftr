# vmxlwaftr Install Guide
 
This step by step guide walks thru the download, build and install of one or more vmxlwaftr Docker Containers serving as AFTR for Lightweight 4over6 on bare metal server.

## Ubuntu Xenial 16.04 (LTS) Server

While any Linux distribution with a a kernel version 3.10 or newer will do, this guide recommends the use of Ubuntu Xenial 16.04 (LTS). 
It is possible to complete the build instructions in a virtual machine, but running the containers will require bare metal support, because Qemu is required to run the Junos vMX within the container and nested hypervisors aren't supported.

## Update and upgrade packages

```
sudo apt update
sudo apt upgrade
```

## Install git and make

Git is used to clone and download a tagged release from GitHub and make will is used to go thru the build steps all the way to the final container.

```
sudo apt install git make
```

## Install Docker engine

Follow the docker-engine install guide on
[https://docs.docker.com/engine/installation/linux/ubuntulinux/]() for Ubuntu 16.04.

Don't forget to add your user accounts that need to build and run the containers to the user group docker in /etc/group.

## Download and build the Container

The automated build instructions together with the download of the required open source projects of specific version of Qemu and Snabb are part of the public repository currently at [https://github.com/mwiget/vmxlwaftr.git](). To get a specific release, e.g. v0.11, use the following command:

```
git clone -b v0.11 https://github.com/mwiget/vmxlwaftr.git
```

This downloads the tagged version (v0.11 in this example) into the directory vmxlwaftr, which must be empty before the command can be run. 
Now change into the new directory and run make:

```
cd vmxlwaftr
make
```

This will take some time, download and build ubuntu development containers to build the various components and finally build the vmxlwaftr container and the optional b4cpe lw4o6 B4 client simulator container.
Details about the build elements can be found here [https://github.com/mwiget/vmxlwaftr/blob/igalia/README.md]().

If successful, you will find the containers ready for use:

```
$ docker images
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
vmxlwaftr           v0.11               14a4d9a46a7c        10 seconds ago      253.2 MB
b4cpe               v0.1                9ac09292c767        2 minutes ago       258.6 MB
build-dumb-init     latest              739c273e6d08        5 minutes ago       347.8 MB
buildqemu           latest              28ddb74e9866        9 minutes ago       432.5 MB
buildsnabb          latest              977a8bee455d        16 minutes ago      344.7 MB
ubuntu              14.04.5             4a725d3b3b1c        2 weeks ago         188 MB
```

## Prepare server for vmxlwaftr launch

The vmxlwaftr container requires at least 4G of available memory hugepages, either of size 2M or 1G. The amount required is directly related to the amount of memory given to the vPFE (VFP) of the vMX via container startup options (default to 4G). You can check the available hugepages via 

```
$ cat /proc/meminfo |grep -i huge
AnonHugePages:   2537472 kB
HugePages_Total:   12000
HugePages_Free:     9995
HugePages_Rsvd:        0
HugePages_Surp:        0
Hugepagesize:       2048 kB
```

If none or not enough are available, create some with the following command (the example allocates 12000 x 2MB equal to 24GB). Never allocate more than the server actually has physical memory!

```
$ sudo sysctl -w vm.nr_hugepages=12000
vm.nr_hugepages = 12000
```

Make the change permanent by updating the kernel boot options via /etc/default/grub and run grub-update:

```
$ grep huge /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="nomodeset hugepages=12000"

$ sudo update-grub

```

## Download vMX from Juniper

Use your Juniper account to download vMX 16.1R1 from Juniper's support site:

[http://www.juniper.net/support/downloads/?p=vmx]()

The file must be present in the same directory from which the container will be launched, which is ~/vmxlwaftr/tests/:

```
$ ls -ln vmx-bundle-16.1R1.7.tgz
-rw-r--r-- 1 1000 1000 3348068041 Sep 11 22:37 vmx-bundle-16.1R1.7.tgz
```

## vMX License keys

Prepare the vMX license keys in a file to be loaded by the container at startup. An example/eval license can be found at the [vMX Free Trial Download Page](http://www.juniper.net/support/downloads/?p=vmx).

## Take it for a virtual spin

### Prepare the virtual network

Now it is time to launch the vmxlwaftr container paired with a B4 test client in another container. To do so, a virtual docker network must be created first and the  server prepared to route traffic between them and to the Internet (via SNAT masquerading). All that is setup up with a small shell script found in the tests directory. Launch it either as root or give the sudo password when asked:

```
$ cd ~/vmxlwaftr/tests/
~/vmxlwaftr/tests$ ./create-lwaftr1-testbed.sh
checking if docker network net-lwaftr1 already exists ... ok
need sudo privileges:
[sudo] password for mwiget:
/home/mwiget/vmxlwaftr/tests
creating network net-lwaftr1 ...ok
adding IPv6 network for lwaftr1 ...  on br-ceb0c9a339d3 ok
adding static route to AFTR fd00:4600:8888::2 via gw fd00:4600:1110::2 ... ok
adding static route to 193.5.1.0/24 via 172.20.0.2 ... ok
Adding SNAT masquerading via interface eth0 all set.
```

### Launch vmxlwaftr container

There is a shell script ready to launch a vmxlwaftr container with a basic configuration with a handful binding entries, all from the same tests directory. Have a look at the script to see what options it needs, particularly the presence of the license file. The Junos config lwfatr1.txt it references is also present in this directory:

```
$ cd cd ~/vmxlwaftr/tests/
~/vmxlwaftr/tests$ ./run-lwaftr1.sh
c814c93868eb16fb9e0730a3bbcc33d02086eb05723797dcd6cea3dc00b047f
Juniper Networks vMX lwaftr Docker Container
vmxlwaftr:v0.11
Sun Sep 11 20:34:53 UTC 2016

Launching with arguments: -I snabbvmx.key -l license-eval.txt -c lwaftr1.txt vmx-bundle-16.1R1.7.tgz

. . . 

FreeBSD/amd64 (lwaftr1) (ttyu0)

login:
```

This will launch the container and provide console access to the vMX VCP (control plane). Note that the device will automatically reboot twice, which is normal and required. There is a default login account ready, username lab, password lab123. Log in and check / wait until the PFE is shown as ready and ge-0/0/0 becomes visible:

```
FreeBSD/amd64 (lwaftr1) (ttyu0)

login: lab
Password:

--- JUNOS 16.1R1.7 Kernel 64-bit  JNPR-10.1-20160624.329953_builder_stable_10
lab@lwaftr1> show chassis fpc
                     Temp  CPU Utilization (%)   CPU Utilization (%)  Memory    Utilization (%)
Slot State            (C)  Total  Interrupt      1min   5min   15min  DRAM (MB) Heap     Buffer
  0  Online           Testing   2         0        1      1      1      1        27          0
  1  Empty
  2  Empty
  3  Empty
  4  Empty
  5  Empty
  6  Empty
  7  Empty
  8  Empty
  9  Empty
 10  Empty
 11  Empty

lab@lwaftr1> show interfaces terse ge-0/0/0
Interface               Admin Link Proto    Local                 Remote
ge-0/0/0                up    up
ge-0/0/0.0              up    up   inet     172.20.0.2/24
                                   inet6    fd00:4600:1110::2/64
                                            fe80::2cf:69ff:fe15:0/64
                                   multiservice

lab@lwaftr1>
```

### Launch the B4 client simulator Docker Container

From another shell, launch the B4 client with the shell script, then try to ping a public host on the Internet, e.g. the Google DNS server at 8.8.8.8. 

```
~/vmxlwaftr/tests$ ./run-b4cpe1.sh

b4cpe:v0.1 Sun Sep 11 20:32:33 UTC 2016

Welcome to the B4 client

My IPv6 address on eth0 is fd00:4600::1001
My IPv6 remote tunnel endpoint (AFTR) is fd00:4600:8888::2
My assigned IPv4 address and port range is 193.5.1.2 1024-2047

Chain POSTROUTING (policy ACCEPT)
target     prot opt source               destination
SNAT       tcp  --  anywhere             anywhere             to:193.5.1.2:1024-2047
SNAT       udp  --  anywhere             anywhere             to:193.5.1.2:1024-2047
SNAT       icmp --  anywhere             anywhere             to:193.5.1.2:1024-2047

root@5e5937635073:/#
root@5e5937635073:/# ping 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=3 ttl=47 time=14.2 ms
64 bytes from 8.8.8.8: icmp_seq=4 ttl=47 time=15.0 ms
64 bytes from 8.8.8.8: icmp_seq=5 ttl=47 time=14.4 ms
64 bytes from 8.8.8.8: icmp_seq=6 ttl=47 time=14.6 ms
^C
--- 8.8.8.8 ping statistics ---
6 packets transmitted, 4 received, 33% packet loss, time 5003ms
rtt min/avg/max/mdev = 14.282/14.582/15.009/0.297 ms
root@5e5937635073:/#
```

More details about the test setup can be found at [https://github.com/mwiget/vmxlwaftr/tree/v0.11/tests]().


