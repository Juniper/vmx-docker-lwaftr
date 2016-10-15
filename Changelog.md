## v1.1.8:

- fixed Error: File "/tmp/snabb_xe0.log" is empty.

## v1.1.7:

- check if vMX has been given any interfaces and terminate if not

## v1.1.6:

- Sync Snabb to igalia/lwaftr commit f6272b03864705dc401f088d6d87c4e3ed2fba0b, Oct 10
- Add fragmentation config knobs in YANG for lwaftr app
- fix typo (Statisitics)

## v1.1.5:

- Increase vMX RE /config disk to 6GB (from 2GB)

## v1.1.4:

- snabb syncd to igalia/lwaftr 7277beca69e50536a1a6d8e861301855e5220a40 (Fri Oct 7 11:42:37 2016 +0200)
- YANG package ID limited to 5 characters (set to lwaft from lwaftr)
- fix monitor lwaftr v4 per second counters
- document lab and root password in test configuration files (lab/lab123 root/lab123)
- Fixed minor issue in the lwaftr monitor & a mutex issue in the daemonized app.
- use snabb_stats.xml provided by JET
- changed formatting output in monitor lwaftr
- use sudo in test scripts for snabb
- fix dynamic rendering for counters in show lwaftr statistics
- enhance support-info doc
- let JET daemon do the statistics gathering
- create test scripts for offline support use

## v1.1.3:

- Updated scripts and yang files for JET

## v1.1.2:

- add submodules and combine bulid in one container 
- remove nexthop.sh. Use snabbvmx query instead
- remove reference to removed nexthop.sh
- updated JET op and snmp script
- remove obsolete directory python-tools
- update Dockerfile with correct snmp python script
- Merge pull request #459 from Igalia/refactor-lwutils
- updated jet scripts
- snabb: latest commit to include Merge pull request #471 from mwiget/snabbvmx-query-id-name
- update Changelog with v1.1.2

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
