# Collect support information

Use the shell script [collect-support-infos.sh](tests/collect-support-infos.sh) to collect Snabb related data from a running container by name:

```
$ ./collect-support-infos.sh lwaftr2
collecting data in container lwaftr2 ...
tar: Removing leading `/' from member names
tar: Removing leading `../' from member names
transferring data from the container to host ...
-rw-r--r-- 1 mwiget mwiget 645364 Sep 13 10:44 support-info-20160913-1044.tgz
```

The collected tar file contains the VERSION, memory, process information, all configuration and binding files (in source and snabb lwaftr format), the current statistic counters and the config drive content used to launch the vMX plus the actual snabb binary. Test launch scripts (test_snabb*.sh) can be used for standalone use.

```
$ 
$ tar ztf support-info-20161001-1011.tgz
VERSION
snabb_xe0.log
snabb_xe1.log
snabb_xe2.log
snabb_xe3.log
mac_xe0
mac_xe1
mac_xe2
mac_xe3
pci_xe0
pci_xe1
pci_xe2
pci_xe3
binding_table_empty.txt
binding_table_xe0.txt
sysinfo.txt
binding_table_xe0.txt.s
snabbvmx-lwaftr-xe0.cfg
test-snabbvmx-lwaftr-xe0.cfg
snabbvmx-lwaftr-xe0.conf
stats.xml
config.new1
config.old
test_snabb_lwaftr_xe0.sh
test_snabb_lwaftr_xe1.sh
test_snabb_lwaftr_xe2.sh
test_snabb_lwaftr_xe3.sh
test_snabb_snabbvmx_xe0.sh
test_snabb_snabbvmx_xe1.sh
test_snabb_snabbvmx_xe2.sh
test_snabb_snabbvmx_xe3.sh
config_drive/vmm-config.tgz
root/.bashrc
usr/local/bin/snabb
```

These files can be used to document and recreate Snabb lwaftr related issues offline.

## Offline troubleshooting

To isolate a potential issue, you can run snabbvmx and lwaftr standalone outside the container. Use the following order of testing:

1. test_snabb_snabbvmx_*.sh runs snabbvmx, honoring settings for fragmentation/reassembly and packet filtering
2. test_snabb_lwaftr_*.sh runs lwaftr, with fragmentation/reassembly always active and no packet filtering

If an issue is seen in lwaftr, report it against lwaftr directly. If an issue is seen only when running snabbvmx, report the issue against snabbvmx. If the issue is only seen in a running container, then the issue can either be a routing or next hop resolution problem. If it is a next hop resolution issue, further rootcause analysis is required to determine the true source of an issue, either in snabbvmx or vMX.

## Run snabbvmx standalone

A script and configuration file has been automatically created that allows the execution of snabbvmx without container and without vMX. It uses a modified version of snabbvmx-lwaftr-xe0.cfg in test-snabbvmx-lwaftr-xe0.cfg, the binding table and snabbvmx-lwaftr-xe0.conf file. The modification turn off next hop resolution via vMX and set a static next hop address of 02:02:02:02:02:02. 
Adjust the next hop address as needed. 

```
$ cat ./test_snabb_snabbvmx_xe0.sh
#!/bin/bash
echo "launching snabb snabbvmx on-a-stick on PCI 0000:03:00.0"
sudo usr/local/bin/snabb snabbvmx lwaftr --conf test-snabbvmx-lwaftr-xe0.cfg --id xe0 --pci 0000:03:00.0 --mac 02:b0:53:89:03:00

$ ./test_snabb_snabbvmx_xe0.sh
launching snabb snabbvmx on-a-stick on PCI 0000:03:00.0
Ring buffer size set to 2048
loading compiled binding table from ./binding_table_60k.txt.s.o
compiled binding table ./binding_table_60k.txt.s.o is up to date.
Hairpinning: no
nic_xe0 ether 02:b0:53:89:03:00
IPv6 fragmentation and reassembly: no
IPv4 fragmentation and reassembly: no
lwAFTR service: enabled
Running without VM (no vHostUser sock_path set)
nh_fwd6: cache_refresh_interval set to 0 seconds
nh_fwd6: static next_hop_mac 02:02:02:02:02:02
loading compiled binding table from ./binding_table_60k.txt.s.o
compiled binding table ./binding_table_60k.txt.s.o is up to date.
nh_fwd4: cache_refresh_interval set to 0 seconds
nh_fwd4: static next_hop_mac 02:02:02:02:02:02
Ingress drop monitor: flush (threshold: 100000 packets; wait: 20 seconds; interval: 1.00 seconds)
```

The application is now ready to process traffic received over the physical interface. Stop the application with ^C.

### Run lwaftr standalone

The script test_snabb_lwaftr_xe0.sh can be used to run just the lwaftr in single stick mode. It uses the binding table and the configuration file snabbvmx-lwaftr-xe0.conf directly. The static next hop for IPv4 and IPv6 is set in that configuration file to 02:02:02:02:02:02. Adjust as needed. 

```
$ cat test_snabb_lwaftr_xe0.sh
#!/bin/bash
echo "launching snabb lwaftr on-a-stick on PCI 0000:03:00.0"
sudo usr/local/bin/snabb lwaftr run --conf snabbvmx-lwaftr-xe0.conf --on-a-stick 0000:03:00.0

$ ./test_snabb_lwaftr_xe0.sh
launching snabb lwaftr on-a-stick on PCI 0000:03:00.0
loading compiled binding table from ./binding_table_60k.txt.s.o
compiled binding table ./binding_table_60k.txt.s.o is up to date.
```

The application is now ready to process traffic received over the physical interface. Stop the application with ^C.

