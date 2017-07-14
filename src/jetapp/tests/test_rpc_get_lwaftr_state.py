#!/usr/bin/python
__author__ = "Amish Anand"
__copyright__ = "Copyright (c) 2015 Juniper Networks, Inc."

"""
This script will be used by the yang file for retrieving the statistics
This has to be run on the VMX by adding this script as an extension-application
"""
import sys
import xmlrpclib
import xml.etree.ElementTree as ET
import getpass 
import os

def PRINT_TAG(node, tag):
    if node.tag == tag:
        print '<'+tag+'>'
	if node.text.strip() == "":
	    print "n/a"
	else:
            print node.text.strip()
        print '</'+tag+'>'
    return

def snabb_state(query_output):
    root = ET.fromstring(query_output)
    print ("<snabb>")
    for instance in root:
        # In each instance, we need to query the id, pci, pid.
        print ("<instance>")
        for child in instance:
            PRINT_TAG(child, "id")
            PRINT_TAG(child,"pid")
	    PRINT_TAG(child,"next_hop_mac_v4")
	    PRINT_TAG(child,"next_hop_mac_v6")
	    #child = None
	    #for child in instance:
	    if child.tag == "pci":
		        for pcis in child:
		            for pci_child in pcis:
                        	PRINT_TAG(pci_child,"rxpackets")
                        	PRINT_TAG(pci_child,"txpackets")
                        	PRINT_TAG(pci_child,"rxdrop")
                        	PRINT_TAG(pci_child,"txdrop")
        print "</instance>"
    print ("</snabb>")
    return
def main(argv):
    """
    Used to fetch the snabb instance information from the JET app.

    :param argv: Arguments for the command
    :return: Dictionary of instances state information
    """
    try:
        server = xmlrpclib.ServerProxy('http://127.0.0.1:9191', verbose=False)
	output = server.lwaftr()
    except Exception as e:
        output = "Failed to connect to jetapp " + e.message+ " user: "+ str(os.geteuid()) 
	print "<snabb><instance><rpc_error>"+output+"</rpc_error></instance></snabb>"
        return
    if (output != None):
        snabb_state(output)
    else:
	print "<snabb><instance><rpc_error>"+output+"</rpc_error></instance></snabb>"

if __name__ == '__main__':
    main(sys.argv)
