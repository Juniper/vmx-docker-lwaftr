
# Juniper Networks vMX lwaftr Docker Container

The vmx-docker-lwaftr Docker Container contains everything thats required to successfully launch vMX 16.1R3 and newer images with a configuration file and license key. This document describes how that Container can be built from source. The actual vMX images is NOT part of the Container. It will be loaded from the official vMX tar file placed in the local directory from where the Container is launched.

Consult the Juniper White Paper on [vMX Lightweight 4over6 Virtual Network Function](https://www.juniper.net/assets/us/en/local/pdf/whitepapers/2000648-en.pdf) for a solution overview and listen to the podcast on Software Gone Wild by Ivan Pepelnjak, Dec 2016: [Blog](http://blog.ipspace.net/2016/12/snabb-switch-with-vmx-control-plane-on.html), [MP3](http://stream.ipspace.net/nuggets/podcast/Show_68-lwAFTR_Snabb_Data_Plane_with_vMX_Control_Plane.mp3).

## Requirements

- [Juniper vMX 17.3 or newer](http://www.juniper.net/support/downloads/?p=vmx)
- Linux kernel 3.13.0+, e.g. as part of Ubuntu 14.04+ or any other Linux distribution
- [Docker Engine 1.12.0+](https://docs.docker.com/engine/installation/)
- [Docker Compose 1.14.0](https://docs.docker.com/compose/install/)
- make (install this e.g. via sudo apt-get make)

## Build instructions

The Container vmx-docker-lwaftr is based on the official Ubuntu Docker 14.04 base Container and includes the following elements:

* Qemu 
* Snabb
* JET Python Client Library

Starting with version 1.2.0, the build process has been simplified, thanks to docker-compose and
Junos 17.3, which allows the forwarding engine to run natively in the Linux container and hence
removes the need for a custom Qemu version. Instead of submodules, specific branches are pulled 
and built as part of the build process.

### Clone repo

[wip] until a 1.2.0 tag is set, clone branch criot from mwiget instead of Juniper.

```
git clone -b criot https://github.com/mwiget/vmx-docker-lwaftr
```

Or to clone a specific version by tag, use git option '-b' to specify a specific tag:

```
git clone -b v1.2.0 https://github.com/juniper/vmx-docker-lwaftr
```

### Install docker-compose

Check if your compute node has docker-compose 1.14.0 or newer installed:

```
$ docker-compose --version
docker-compose version 1.14.0, build c7bdf9e
```

Otherwise download it:

```
$ sudo su -
# curl -L https://github.com/docker/compose/releases/download/1.14.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
# chmod a+rx /usr/local/bin/docker-compose
# exit
$ docker-compose --version
docker-compose version 1.14.0, build c7bdf9e
```

### Build Containers

The build process is now managed via the [docker-compose.yml](docker-compose.yml) file. 
In addition, a [Makefile](Makefile) is also provided to drive the various docker-compose tools
with make, but its use is optional.

```
docker-compose build
```

This will take several minutes and requires Internet access. Alternatively, use 'make build'.
Use 'docker-compose images' to 
show the various containers built:


```
$ docker-compose images
Container                       Repository              Tag       Image Id      Size
-------------------------------------------------------------------------------------------------
vmxdockerlwaftr_b4cpe_1           vmxdockerlwaftr_b4cpe           latest   62dcf1646dd4   248 MB
vmxdockerlwaftr_lwaftr_1          vmxdockerlwaftr_lwaftr          latest   93ced775afe5   510 MB
vmxdockerlwaftr_packetblaster_1   vmxdockerlwaftr_packetblaster   latest   efc7db6754eb   13.7 MB
vmxdockerlwaftr_server_1          vmxdockerlwaftr_server          latest   6c60bb084491   18.5 MB
```

| Container Image | Description |
|---|--|
| vmxdockerlwaftr_lwaftr_1 | Main container to launch Junos vMX image |
| vmxdockerlwaftr_packetblaster_1 | Generates low PPS traffic into xe-0/0/0 over linux bridges |
| vmxdockerlwaftr_b4cpe_1 | B4 test client for one subscriber connected to xe-0/0/1 |
| vmxdockerlwaftr_server_1 | Test server for the B4 client to ping and query via http at 1.1.1.1 |

### Save vmx-docker-lwaftr Container to file

Optional. Save the vmx-docker-lwaftr Container into an image file for transfer to a compute node without Internet connectivity:

```
$ docker save -o vmx-docker-lwaftr-v1.2.0.img vmxdockerlwaftr_lwaftr
mwiget@sa:~/vmx-docker-lwaftr$ ls -l vmx-docker-lwaftr-v1.2.0.img
-rw------- 1 mwiget mwiget 541005824 Jul 16 15:50 vmx-docker-lwaftr-v1.2.0.img
```

## Running the vmx-docker-lwaftr Container

Before launching it, you need provide the Junos qcow2 image from the vmx-bundle tar file, a license key and a ssh public key to access the instance once running.
Place these three files into the top directory of the cloned repo.

### Download and extract junos*qcow2

Download vMX 17.3 or newer from Juniper, then extract the junos*qcow2 Junos image. Nothing else is required. The forwarding engine will be downloaded from the control plane automatically. 

```
$ tar zxf vmx-bundle-17.3B1.1.tgz
$ mv vmx/images/junos-vmx-x86-64-17.3B1.1.qcow2 .
$ rm -rf vmx
$ ls -l junos-vmx-x86-64-17.3B1.1.qcow2
-rw-r--r-- 1 mwiget mwiget 1226440704 Jun 22 00:14 junos-vmx-x86-64-17.3B1.1.qcow2
```

### Download license key

Download the [vMX eval license key from Juniper](https://www.juniper.net/us/en/dm/free-vmx-trial/):

```
$ wget  https://www.juniper.net/us/en/dm/free-vmx-trial/E421992502.txt
--2017-07-16 16:05:40--  https://www.juniper.net/us/en/dm/free-vmx-trial/E421992502.txt
Resolving www.juniper.net (www.juniper.net)... 2a02:26f0:78:198::720, 2a02:26f0:78:181::720, 95.101.252.154
Connecting to www.juniper.net (www.juniper.net)|2a02:26f0:78:198::720|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 206 [text/plain]
Saving to: ‘E421992502.txt’

E421992502.txt            100%[==================================>]     206  --.-KB/s    in 0s

2017-07-16 16:05:40 (359 MB/s) - ‘E421992502.txt’ saved [206/206]

$ mv E421992502.txt license-eval.txt
```

If you have a production key, use that one instead and adjust the license key file name in the [docker-compose.yml](docker-compose.yml) file.

### Copy your ssh public key

Each instance will create a random root password, accessible via 'docker logs <instance-id>'. To access the instance via ssh public/private key, copy your ssh public key file to the repo root directory:

```
$ cp ~/.ssh/id_rsa.pub .
```

### Launch instance

The launch of the instance is done via 'docker-compose up -d'. The option '-d' is needed to launch the instance in the background. The use of 'make up' is a shorter version to type, but uses the same command. It builds the container image again if needed too.

Check the content of [docker-compose.yml](docker-compose.yml) to understand what exactly gets built and launched. It serves as an example and will need adjustment. "out-of-the-box" it launches one lwaftr (vMX) instance, a packetblaster traffic generator for 60k subscribers into 0/0/0 and a b4cpe client, which can be used to interactively test the functionality via 0/0/1 by pinging and connecting to 1.1.1.1 via HTTP.

```
$ make up
docker-compose build
Building lwaftr
Step 1/22 : FROM ubuntu:14.04
 ---> 4a2820e686c4
Step 2/22 : LABEL maintainer Juniper Networks
 ---> Using cache
 ---> b304d31999c8
. . .
Successfully built d3b692e019aa
Successfully tagged vmxdockerlwaftr_server:latest
docker-compose up -d
Creating network "vmxdockerlwaftr_default" with the default driver
Creating network "vmxdockerlwaftr_net-xe0" with the default driver
Creating network "vmxdockerlwaftr_net-xe1" with the default driver
Creating vmxdockerlwaftr_lwaftr_1 ...
Creating vmxdockerlwaftr_lwaftr_1 ... done
Creating vmxdockerlwaftr_packetblaster_1 ...
Creating vmxdockerlwaftr_server_1 ...
Creating vmxdockerlwaftr_b4cpe_1 ...
Creating vmxdockerlwaftr_b4cpe_1
Creating vmxdockerlwaftr_server_1
Creating vmxdockerlwaftr_server_1 ... done
$
```

This creates the required management network, networks with default driver for xe0 and xe1, a packetblaster, b4cpe client and server to test the functionality, and finally the vMX itself. 

The [Makefile](Makefile) contains shortcuts to various useful functions. It is worth to explore this file to understand how these commands can be used directly.

### Check the status 

```
$ make ps
docker-compose ps
             Name                            Command               State                       Ports
------------------------------------------------------------------------------------------------------------------------
vmxdockerlwaftr_b4cpe_1           /launch.sh 193.5.1.2 1024- ...   Up
vmxdockerlwaftr_lwaftr_1          /usr/bin/dumb-init -- /usr ...   Up      0.0.0.0:32905->22/tcp, 0.0.0.0:32904->830/tcp
vmxdockerlwaftr_packetblaster_1   /launch.sh --b4 2001:db8:: ...   Up
vmxdockerlwaftr_server_1          /launch.sh                       Up
```

If one of the instances is down, check its log file. For the main vmxdockerlwaftr_lwaftr_1 instance, a short cut is provided:

```
$ make logs
docker logs -f $(docker ps -a|grep _lwaftr|cut -d' ' -f1)
Juniper Networks vMX lwaftr Docker Container Sun Jul 16 14:12:59 UTC 2017

/u contains the following files:
Changelog.md	 b4cpe			id_rsa.pub			 server
LICENSE		 binding_table_60k.txt	junos-vmx-x86-64-17.3B1.1.qcow2  snabb
Makefile	 docker-compose.yml	license-eval.txt		 src
README.md	 dumb-init		lwaftr.conf.txt
SUPPORT-INFO.md  getpass.sh		packetblaster
Launching with arguments:
02:42:ac:14:01:10 02:42:ac:14:02:10
02:42:ac:14:01:10 eth0 -> eth1
02:42:ac:14:02:10 eth0 -> eth2
-----------------------------------------------------------------------
vMX vmxdockerlwaftr_lwaftr_1 (172.18.0.2) root password laenohneiraiquiucujehuro
-----------------------------------------------------------------------

using qcow2 image junos-vmx-x86-64-17.3B1.1.qcow2
using license keys in license-eval.txt
ethernet interfaces: eth0 eth1 eth2
creating ssh public/private keypair to communicate with Junos
Generating public/private rsa key pair.
. . .
```

The command does a 'tail -f' on the log file to monitor progress. Hit 'Ctrl-C' to terminate this command (the instance will keep running).

Note the auto-generated root password. This is required to log in to the console.

### Access vMX via console

Use 'make attach' to not only connect to the vMX serial console, but to also display the root password of the instance for copy-paste:

```
$ make attach
./getpass.sh | grep lwaftr
vmxdockerlwaftr_lwaftr_1: vMX vmxdockerlwaftr_lwaftr_1 (172.18.0.2) root password laenohneiraiquiucujehuro
docker attach $(docker ps |grep _lwaftr|cut -d' ' -f1)


FreeBSD/amd64 (vmxdockerlwaftr_lwaftr_1) (ttyu0)

login: root
Password:

--- JUNOS 17.3B1.1 Kernel 64-bit  JNPR-10.3-20170605.150032_fbsd-
At least one package installed on this device has limited support.
Run 'file show /etc/notices/unsupported.txt' for details.
root@vmxdockerlwaftr_lwaftr_1:~ # cli
root@vmxdockerlwaftr_lwaftr_1>

```

Hit Ctrl-P Ctrl-Q, followed by Ctrl-C to detach from the console.

### Check lw4o6 traffic

An easy shortcut to display the snabb lwaftr counters is provided via 'make query':

```
$ make query

xe0: lwAFTR operational counters (non-zero)
in-ipv4-bytes:    230,062,862
in-ipv4-packets:  1,620,161
in-ipv6-bytes:    294,869,302
in-ipv6-packets:  1,620,161
out-ipv4-bytes:   230,062,862
out-ipv4-packets: 1,620,161
out-ipv6-bytes:   294,869,302
out-ipv6-packets: 1,620,161

xe1: lwAFTR operational counters (non-zero)

xe2: (missing)

xe3: (missing)
```

Above example was taken from an instance running in simulation mode without any PCI interfaces connected.

Launch the b4cpe console, ping 1.1.1.1 and download the index.html file from the web server provided by the container [server](server) at IP address 1.1.1.1. Exit the client and check the lwaftr counters again. You should see a handful packets reported on xe1 (0/0/1):

```
$ make cpe
docker exec -ti $(docker ps | grep b4cpe|cut -d' ' -f1) bash
root@72069c7cff5b:/# ping 1.1.1.1
PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.
64 bytes from 1.1.1.1: icmp_seq=1 ttl=63 time=2.13 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=63 time=1.93 ms
64 bytes from 1.1.1.1: icmp_seq=3 ttl=63 time=1.97 ms
64 bytes from 1.1.1.1: icmp_seq=4 ttl=63 time=2.91 ms
^C
--- 1.1.1.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3003ms
rtt min/avg/max/mdev = 1.937/2.240/2.916/0.401 ms
root@72069c7cff5b:/# wget 1.1.1.1
--2017-07-16 14:29:01--  http://1.1.1.1/
Connecting to 1.1.1.1:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 91 [text/html]
Saving to: 'index.html'

100%[==================================================================================================================================================================>] 91          --.-K/s   in 0s

2017-07-16 14:29:01 (11.7 MB/s) - 'index.html' saved [91/91]

root@72069c7cff5b:/# cat index.html

682197badb86 - container server running
Using lwaftr at 172.20.2.16 as default gateway.

root@72069c7cff5b:/# exit
exit
mwiget@xeon:~/vmx-docker-lwaftr$ make query

xe0: lwAFTR operational counters (non-zero)
in-ipv4-bytes:    2,101,976,726
in-ipv4-packets:  14,802,653
in-ipv6-bytes:    2,694,090,308
in-ipv6-packets:  14,802,694
out-ipv4-bytes:   2,101,982,548
out-ipv4-packets: 14,802,694
out-ipv6-bytes:   2,694,082,846
out-ipv6-packets: 14,802,653

xe1: lwAFTR operational counters (non-zero)
in-ipv4-bytes:    1,067
in-ipv4-packets:  9
in-ipv6-bytes:    1,439
in-ipv6-packets:  11
out-ipv4-bytes:   999
out-ipv4-packets: 11
out-ipv6-bytes:   1,427
out-ipv6-packets: 9

xe2: lwAFTR operational counters (non-zero)

xe3: lwAFTR operational counters (non-zero)
```

The counters can also be checked, in a different format, on the vMX CLI:

```
root@vmxdockerlwaftr_lwaftr_1> op lwaftr
Id  Pid   Nexthop v4        Nexthop v6           rxPackets   txPackets   rxDrops   txDrops
0   971   02:42:ac:14:01:fe 02:42:ac:14:01:fe     32281024    32281050                   0
1   991   00:00:00:00:00:00 00:00:00:00:00:00           43         811                   0
2   995   00:00:00:00:00:00 00:00:00:00:00:00            0         125         0         0
3   1022  00:00:00:00:00:00 00:00:00:00:00:00            0         125         0         0
```

