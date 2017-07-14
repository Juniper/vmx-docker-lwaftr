#!/usr/bin/python
__author__ = "Amish Anand"
__copyright__ = "Copyright (c) 2015 Juniper Networks, Inc."

"""
This script will be used by the yang file for retrieving the statistics
"""
import sys
import xmlrpclib
import xml.etree.ElementTree as ET

def PRINT_TAG(node, tag):
    if node.tag == tag:
        print '<'+tag+'>'
	if node.text.strip() == "":
	    print "n/a"
	else:
            print node.text.strip()
        print '</'+tag+'>'
    return

def stats_per_instance(instance):
        print ("<statistics>")
        for child_instance in instance:
            PRINT_TAG(child_instance,"id")
            if child_instance.tag == "apps":
                for app_child in child_instance:
                    if app_child.tag == "lwaftr":
                        for lwaftr_child in app_child:
                            # Parse all the attributes and print it
                            #print "PRINT_TAG(lwaftr_child,'"+lwaftr_child.tag+"')"
                            PRINT_TAG(lwaftr_child,'drop-all-ipv4-iface-bytes')
                            PRINT_TAG(lwaftr_child,'drop-all-ipv4-iface-packets')
                            PRINT_TAG(lwaftr_child,'drop-all-ipv6-iface-bytes')
                            PRINT_TAG(lwaftr_child,'drop-all-ipv6-iface-packets')
                            PRINT_TAG(lwaftr_child,'drop-bad-checksum-icmpv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-bad-checksum-icmpv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-in-by-policy-icmpv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-in-by-policy-icmpv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-in-by-policy-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-in-by-policy-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-in-by-rfc7596-icmpv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-in-by-rfc7596-icmpv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-ipv4-frag-invalid-reassembly')
                            PRINT_TAG(lwaftr_child,'drop-ipv4-frag-random-evicted')
                            PRINT_TAG(lwaftr_child,'drop-ipv6-frag-invalid-reassembly')
                            PRINT_TAG(lwaftr_child,'drop-ipv6-frag-random-evicted')
                            PRINT_TAG(lwaftr_child,'drop-misplaced-not-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-misplaced-not-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-misplaced-not-ipv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-misplaced-not-ipv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-no-dest-softwire-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-no-dest-softwire-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-no-source-softwire-ipv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-no-source-softwire-ipv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-out-by-policy-icmpv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-out-by-policy-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-over-mtu-but-dont-fragment-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-over-mtu-but-dont-fragment-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-over-rate-limit-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-over-rate-limit-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-over-time-but-not-hop-limit-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-over-time-but-not-hop-limit-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-too-big-type-but-not-code-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-too-big-type-but-not-code-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-ttl-zero-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-ttl-zero-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-unknown-protocol-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-unknown-protocol-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-unknown-protocol-ipv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-unknown-protocol-ipv6-packets')
                            PRINT_TAG(lwaftr_child,'hairpin-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'hairpin-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'in-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'in-ipv4-frag-needs-reassembly')
                            PRINT_TAG(lwaftr_child,'in-ipv4-frag-reassembled')
                            PRINT_TAG(lwaftr_child,'in-ipv4-frag-reassembly-unneeded')
                            PRINT_TAG(lwaftr_child,'in-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'in-ipv6-bytes')
                            PRINT_TAG(lwaftr_child,'in-ipv6-frag-needs-reassembly')
                            PRINT_TAG(lwaftr_child,'in-ipv6-frag-reassembled')
                            PRINT_TAG(lwaftr_child,'in-ipv6-frag-reassembly-unneeded')
                            PRINT_TAG(lwaftr_child,'in-ipv6-packets')
                            PRINT_TAG(lwaftr_child,'ingress-packet-drops')
                            PRINT_TAG(lwaftr_child,'memuse-ipv4-frag-reassembly-buffer')
                            PRINT_TAG(lwaftr_child,'memuse-ipv6-frag-reassembly-buffer')
                            PRINT_TAG(lwaftr_child,'out-icmpv4-bytes')
                            PRINT_TAG(lwaftr_child,'out-icmpv4-packets')
                            PRINT_TAG(lwaftr_child,'out-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'out-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'out-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'out-ipv4-frag')
                            PRINT_TAG(lwaftr_child,'out-ipv4-frag-not')
                            PRINT_TAG(lwaftr_child,'out-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'out-ipv6-bytes')
                            PRINT_TAG(lwaftr_child,'out-ipv6-frag')
                            PRINT_TAG(lwaftr_child,'out-ipv6-frag-not')
                            PRINT_TAG(lwaftr_child,'out-ipv6-packets')
        print "</statistics>"

def snabb_statistics(output,argv):
    root = ET.fromstring(output)
    print "<snabb>"
    found = 0
    instance_id = ""
    for i in range(0,len(argv)):
        if argv[i] == "id":
            instance_id = argv[i+1]
            break

    for instance in root:
        if instance_id != '' and instance.findall("./id")[0].text != argv[2]:
            pass
        else:
	    found += 1
            stats_per_instance(instance)

    if found == 0:
        print "<statistics><id_error>no instance found</id_error></statistics>"
    print "</snabb>"
    return


def main(argv):
    """
    Parse the arguments to determine if the call is for showing the
    statistics of all or one instance.
    :param argv: Arguments for the command
    :return: Dictionary of instances or statistics
    """
    try:
        server = xmlrpclib.ServerProxy('http://127.0.0.1:9191', verbose=False)
        output = server.lwaftr()
    except Exception as e:
        output = "Failed to connect to jetapp " + e.message+ " user: "+ str(os.geteuid())
        print "<snabb><instance><rpc_error>"+output+"</rpc_error></instance></snabb>"
        return
    if (output != None):
	snabb_statistics(output,argv)
    else:
        print "<snabb><instance><rpc_error>"+output+"</rpc_error></instance></snabb>"

if __name__ == '__main__':
    main(sys.argv)
