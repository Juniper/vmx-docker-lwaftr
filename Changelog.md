## v1.1.1:

- add submodules and combine bulid in one container 
- remove nexthop.sh. Use snabbvmx query instead
- remove reference to removed nexthop.sh
- updated JET op and snmp script
- remove obsolete directory python-tools
- update Dockerfile with correct snmp python script
- point to snabb lwaftr branch via submodule: latest commit
- Merge pull request #459 from Igalia/refactor-lwutils
- updated jet scripts
- update Changelog with v1.2.0

## v1.1.0:

- fix lwaftr4 config and use of daily build for testing
- add copyright notice
- add JET opserver and show scripts
- upgrade snabb to snabbvmx-v1.1, tag as v1.1.0

## v1.0.2:

- collect snabb binary with collect-support-infos.sh
- update SUPPORT-INFO.md with adding snabb binary to tgz file
- make jnx-aug-softwire:ipv4_address mandatory
- fix detecting binding table file changes in snabbvmx_manager.pl
- upgraded configs to 16.1R2

## v1.0.1:

- fix numanode warning when launched with 82599 NICs on socket > 0
- Merge branch 'igalia' of https://github.com/mwiget/vmxlwaftr into igalia
- to include snabb Fix update of ingress-packet-drops counter #449
- fix condition when DEBUG isn't defined
- collect also /tmp/config.* files with collect-support-infos.sh
- create empty binding table if instance doesn't have any defined
- remove snabbvmx configs when br instance is no longer configured
- added description to various augmented softwire leafs

## v1.0:
- using Snabb tag lwaftr-snabbvmx-v1.0 from https://github.com/igalia/snabb
