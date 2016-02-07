## Juniper Networks vMX lwaftr Docker Container

Usage:

docker run --name <name> --rm -v \$PWD:/u:ro \\
   --privileged -i -t marcelwiget/vmxlwaftr[:version] [-C <core>] \\
   -c <junos_config_file> -i identity [-l license_file] \\
   [-m <kbytes>] <image> <pci-address> [<pci-address> ...]

[:version]       Container version. Defaults to :latest

 -v \$PWD:/u:ro   Required to access a file in the current directory
                 docker is executed from (ro forces read-only access)
                 The file will be copied from this location

 -l  license_file to be loaded at startup (requires user snabbvmx with ssh
     private key given via option -i)

 -i  ssh private key for user snabbvmx 
     (required to access lwaftr config via netconf)

 -m  Specify the amount of memory for the vRE (default 8000kB)
 -C  pin snabb to a specific core(s) (in taskset -c format, defaults to 0)

 -d  Enable debug shell (launched before and after qemu runs)

<pci-address>    PCI Address of the Intel 825999 based 10GE port
                 Multiple ports can be specified, space separated

Example:
docker run --name lwaftr1 --rm --privileged -v \$PWD:/u:ro \\
  -i -t marcelwiget/vmxlwaftr -c lwaftr1.txt -i snabbvmx.key \\
  jinstall64-vrr-14.2R5.8-domestic.img 0000:05:00.0 0000:05:00.0

