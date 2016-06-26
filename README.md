## Juniper Networks vMX lwaftr Docker Container

Usage:

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

