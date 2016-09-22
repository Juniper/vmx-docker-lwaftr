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

The collected tar file contains the VERSION, memory, process information, all configuration and binding files (in source and snabb lwaftr format), the current statistic counters and the config drive content used to launch the vMX plus the actual snabb binary. E.g.:

```
$ tar ztf support-info-20160913-1044.tgz
VERSION
mac_xe0
pci_xe0
binding_table_60k.txt
sysinfo.txt
binding_table_60k.txt.s
snabbvmx-lwaftr-xe0.cfg
snabbvmx-lwaftr-xe0.conf
stats.xml
config_drive/vmm-config.tgz
root/.bashrc
usr/local/bin/snabb
```

These files can be used to document and recreate Snabb lwaftr related issues offline.



