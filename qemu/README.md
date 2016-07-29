apply snabb reconnect patch:
cd build
patch -p1 < ../qemu-snabb.diff


The standard upstream QEMU should be fine except for one aspect: it does not allow the vswitch to restart and reconnect to a virtual machine. (If you restart Snabb Switch then the VMs will not process traffic until you restart them too.) This is unfortunate: I like being able to restart at any time.

The origin of this patch is
https://github.com/snabbco/qemu/commit/c9cea8f431c929f70a9371f4b379ab66c15c5293

Nikolay from Virtual Open Systems tried to get this pach upstreamed into Qemu, but the developers of Qemu declined.

See also http://www.virtualopensystems.com/en/solutions/guides/snabbswitch-qemu/

It looks as if this issue is being worked on by qemu-devel, but couldn't find out what release will have the fix:
https://lists.gnu.org/archive/html/qemu-devel/2016-07/msg04922.html

