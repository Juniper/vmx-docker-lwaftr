# -*- coding: utf-8 -*-
import os
import xmlrpclib
import xml.etree.ElementTree as ET
import time
import sys
import select
import threading
import datetime
import jcs

timeout = 1 # seconds
read_list = [sys.stdin]

SNABB_V6_TEMPLATE = r"""
Current Time: %s
                                                                   Total           per second
 lwaftr_v6 in-ipv6-packets                                            %6s                   %6s
 lwaftr_v6 in-ipv6-bytes                                              %6s                   %6s
 lwaftr_v6 out-ipv6-packets                                           %6s                   %6s
 lwaftr_v6 out-ipv6-bytes                                             %6s                   %6s
 lwaftr_v6 drop-all-ipv6-iface-packets                                %6s                   %6s
 lwaftr_v6 in-ipv6-frag-reassembled                                   %6s                   %6s
 lwaftr_v6 drop-ipv6-frag-invalid-reassembly                          %6s                   %6s
 lwaftr_v6 out-ipv6-frag                                              %6s                   %6s
 lwaftr_v6 out-ipv6-frag-not                                          %6s                   %6s

"""
SNABB_V4_TEMPLATE = r"""
                                                                   Total           per second
 nic ifInDiscards                                                     %6s                   %6s

                                                                   Total           per second
 lwaftr_v4 in-ipv4-packets                                            %6s                   %6s
 lwaftr_v4 in-ipv4-bytes                                              %6s                   %6s
 lwaftr_v4 out-ipv4-packets                                           %6s                   %6s
 lwaftr_v4 out-ipv4-bytes                                             %6s                   %6s
 lwaftr_v4 drop-all-ipv4-iface-packets                                %6s                   %6s
 lwaftr_v4 in-ipv4-frag-reassembled                                   %6s                   %6s
 lwaftr_v4 drop-ipv4-frag-invalid-reassembly                          %6s                   %6s
 lwaftr_v4 out-ipv4-frag                                              %6s                   %6s
 lwaftr_v4 out-ipv4-frag-not                                          %6s                   %6s
 """

class lwaftr_stats:
    def __init__(self):
        self.lwaftr_v4_rx = "0.00"
        self.lwaftr_v4_tx = "0.00"
        self.lwaftr_v4_txdrop = "0.00"
        self.lwaftr_v6_rx = "0.00"
        self.lwaftr_v6_tx = "0.00"
        self.lwaftr_v6_txdrop = "0.00"

        #Ipv6 cumulative counters
        self.lwaftr_v6_in_ipv6_packets = "0.0"
        self.lwaftr_v6_in_ipv6_bytes = "0.0"
        self.lwaftr_v6_out_ipv6_packets = "0.0"
        self.lwaftr_v6_out_ipv6_bytes = "0.0"
        self.lwaftr_v6_drop_all_ipv6_iface_packets = "0.0"
        self.lwaftr_v6_in_ipv6_frag_reassembled = "0.0"
        self.lwaftr_v6_drop_ipv6_frag_invalid_reassembly = "0.0"
        self.lwaftr_v6_out_ipv6_frag = "0.0"
        self.lwaftr_v6_out_ipv6_frag_not = "0.0"
        #Ipv4 cumulative counters
        self.lwaftr_v4_out_ipv4_packets = "0.0"
        self.lwaftr_v4_out_ipv4_bytes = "0.0"
        self.lwaftr_v4_drop_all_ipv4_iface_packets = "0.0"
        self.lwaftr_v4_in_ipv4_frag_reassembled = "0.0"
        self.lwaftr_v4_drop_ipv4_frag_invalid_reassembly = "0.0"
        self.lwaftr_v4_out_ipv4_frag = "0.0"
        self.lwaftr_v4_out_ipv4_frag_not = "0.0"

        #Ipv6 per-second counters
        self.lwaftr_v6_in_ipv6_packets_ps  = "0.0"
        self.lwaftr_v6_in_ipv6_bytes_ps  = "0.0"
        self.lwaftr_v6_out_ipv6_packets_ps  = "0.0"
        self.lwaftr_v6_out_ipv6_bytes_ps  = "0.0"
        self.lwaftr_v6_drop_all_ipv6_iface_packets_ps  = "0.0"
        self.lwaftr_v6_in_ipv6_frag_reassembled_ps  = "0.0"
        self.lwaftr_v6_drop_ipv6_frag_invalid_reassembly_ps  = "0.0"
        self.lwaftr_v6_out_ipv6_frag_ps  = "0.0"
        self.lwaftr_v6_out_ipv6_frag_not_ps  = "0.0"
        #IPv4 per-second counters
        self.lwaftr_v4_in_ipv4_packets  = "0.0"
        self.lwaftr_v4_in_ipv4_packets_ps  = "0.0"
        self.lwaftr_v4_in_ipv4_bytes  = "0.0"
        self.lwaftr_v4_in_ipv4_bytes_ps  = "0.0"
        self.lwaftr_v4_out_ipv4_packets_ps  = "0.0"
        self.lwaftr_v4_out_ipv4_bytes_ps  = "0.0"
        self.lwaftr_v4_drop_all_ipv4_iface_packets_ps  = "0.0"
        self.lwaftr_v4_in_ipv4_frag_reassembled_ps  = "0.0"
        self.lwaftr_v4_drop_ipv4_frag_invalid_reassembly_ps  = "0.0"
        self.lwaftr_v4_out_ipv4_frag_ps  = "0.0"
        self.lwaftr_v4_out_ipv4_frag_not_ps  = "0.0"
        self.lwaftr_ifInDiscards = "0.0"
        self.lwaftr_ifInDiscards_ps = "0.0"

        #Old counters to calculate the ps values
        self.lwaftr_v6_in_ipv6_packets_old = "0.0"
        self.lwaftr_v6_in_ipv6_bytes_old = "0.0"
        self.lwaftr_v6_out_ipv6_packets_old = "0.0"
        self.lwaftr_v6_out_ipv6_bytes_old = "0.0"
        self.lwaftr_v6_drop_all_ipv6_iface_packets_old = "0.0"
        self.lwaftr_v6_in_ipv6_frag_reassembled_old = "0.0"
        self.lwaftr_v6_drop_ipv6_frag_invalid_reassembly_old = "0.0"
        self.lwaftr_v6_out_ipv6_frag_old = "0.0"
        self.lwaftr_v6_out_ipv6_frag_not_old = "0.0"
	self.lwaftr_v4_in_ipv4_packets_old = "0.0"
        self.lwaftr_v4_out_ipv4_packets_old = "0.0"
        self.lwaftr_v4_out_ipv4_bytes_old = "0.0"
        self.lwaftr_v4_in_ipv4_bytes_old = "0.0"
        self.lwaftr_v4_drop_all_ipv4_iface_packets_old = "0.0"
        self.lwaftr_v4_in_ipv4_frag_reassembled_old = "0.0"
        self.lwaftr_v4_drop_ipv4_frag_invalid_reassembly_old = "0.0"
        self.lwaftr_v4_out_ipv4_frag_old = "0.0"
        self.lwaftr_v4_out_ipv4_frag_not_old = "0.0"
        self.lwaftr_ifInDiscards_old = "0.0"
        self.previous_poll = 0


    def set_values(self, node, tag, newval, oldval, psval, newtime):
        if node.tag == tag:
            if node.text.strip() == "":
                #Will not change the value
                oldval = 0
                newval = 0
                oldpsval = 0
                return
            else:
                oldval = newval
                newval = node.text.strip()
                if self.previous_poll != 0:
                    delta = newtime - self.previous_poll
                    nwval = float(newval)-float(oldval)
		    psval = str(nwval/delta)
                else:
                    psval = 0
            return

    def monitor(self, server):
        try:
            newstats = server.lwaftr()
        except Exception as e:
            jcs.output("%s" %e.message)
            exit(0)
        # newstats contains all the latest stats
        newtime = time.time()
        root = ET.fromstring(newstats)
        for instance in root:
            for child_instance in instance:
                if child_instance.tag == "apps":
                    for app_child in child_instance:
                        if app_child.tag == "lwaftr":
                            for lwaftr_child in app_child:
                                self.set_values(lwaftr_child,"in-ipv6-packets",
                                                self.lwaftr_v6_in_ipv6_packets, self.lwaftr_v6_in_ipv6_packets_old,
                                                self.lwaftr_v6_in_ipv6_packets_ps, newtime)
                                self.set_values(lwaftr_child,"in-ipv4-packets",
                                                self.lwaftr_v4_in_ipv4_packets, self.lwaftr_v4_in_ipv4_packets_old,
                                                self.lwaftr_v4_in_ipv4_packets_ps, newtime)
                                self.set_values(lwaftr_child,"in-ipv6-bytes",
                                                self.lwaftr_v6_in_ipv6_bytes, self.lwaftr_v6_in_ipv6_bytes_old,
                                                self.lwaftr_v6_in_ipv6_bytes_ps, newtime)
                                self.set_values(lwaftr_child,"in-ipv4-bytes",
                                                self.lwaftr_v4_in_ipv4_bytes, self.lwaftr_v4_in_ipv4_bytes_old,
                                                self.lwaftr_v4_in_ipv4_bytes_ps, newtime)

                                self.set_values(lwaftr_child,"out-ipv6-packets",
                                                self.lwaftr_v6_out_ipv6_packets, self.lwaftr_v6_out_ipv6_packets_old,
                                                self.lwaftr_v6_out_ipv6_packets_ps, newtime)
                                self.set_values(lwaftr_child,"out-ipv4-packets",
                                                self.lwaftr_v4_out_ipv4_packets, self.lwaftr_v4_out_ipv4_packets_old,
                                                self.lwaftr_v4_out_ipv4_packets_ps, newtime)
                                self.set_values(lwaftr_child,"out-ipv6-bytes",
                                                self.lwaftr_v6_out_ipv6_bytes, self.lwaftr_v6_out_ipv6_bytes_old,
                                                self.lwaftr_v6_out_ipv6_bytes_ps, newtime)
                                self.set_values(lwaftr_child,"out-ipv4-bytes",
                                                self.lwaftr_v4_out_ipv4_bytes, self.lwaftr_v4_out_ipv4_bytes_old,
                                                self.lwaftr_v4_out_ipv4_bytes_ps, newtime)

                                self.set_values(lwaftr_child,"drop-all-ipv6-iface-packets",
                                                self.lwaftr_v6_drop_all_ipv6_iface_packets, self.lwaftr_v6_drop_all_ipv6_iface_packets_old,
                                                self.lwaftr_v6_drop_all_ipv6_iface_packets_ps, newtime)
                                self.set_values(lwaftr_child,"drop-all-ipv4-iface-packets",
                                                self.lwaftr_v4_drop_all_ipv4_iface_packets, self.lwaftr_v4_drop_all_ipv4_iface_packets_old,
                                                self.lwaftr_v4_drop_all_ipv4_iface_packets_ps, newtime)

                                self.set_values(lwaftr_child,"in-ipv6-frag-reassembled",
                                                self.lwaftr_v6_in_ipv6_frag_reassembled, self.lwaftr_v6_in_ipv6_frag_reassembled_old,
                                                self.lwaftr_v6_in_ipv6_frag_reassembled_ps, newtime)
                                self.set_values(lwaftr_child,"in-ipv4-frag-reassembled",
                                                self.lwaftr_v4_in_ipv4_frag_reassembled, self.lwaftr_v4_in_ipv4_frag_reassembled_old,
                                                self.lwaftr_v4_in_ipv4_frag_reassembled_ps, newtime)
                                self.set_values(lwaftr_child,"drop-ipv6-frag-invalid-reassembly",
                                                self.lwaftr_v6_drop_ipv6_frag_invalid_reassembly, self.lwaftr_v6_drop_ipv6_frag_invalid_reassembly_old,
                                                self.lwaftr_v6_drop_ipv6_frag_invalid_reassembly_ps, newtime)
                                self.set_values(lwaftr_child,"drop-ipv4-frag-invalid-reassembly",
                                                self.lwaftr_v4_drop_ipv4_frag_invalid_reassembly, self.lwaftr_v4_drop_ipv4_frag_invalid_reassembly_old,
                                                self.lwaftr_v4_drop_ipv4_frag_invalid_reassembly_ps, newtime)
                                self.set_values(lwaftr_child,"out-ipv6-frag",
                                                self.lwaftr_v6_out_ipv6_frag, self.lwaftr_v6_out_ipv6_frag_old,
                                                self.lwaftr_v6_out_ipv6_frag_ps, newtime)
                                self.set_values(lwaftr_child,"out-ipv4-frag",
                                                self.lwaftr_v4_out_ipv4_frag, self.lwaftr_v4_out_ipv4_frag_old,
                                                self.lwaftr_v4_out_ipv4_frag_ps, newtime)
                                self.set_values(lwaftr_child,"out-ipv6-frag-not",
                                                self.lwaftr_v6_out_ipv6_frag_not, self.lwaftr_v6_out_ipv6_frag_not_old,
                                                self.lwaftr_v6_out_ipv6_frag_not_ps, newtime)
                                self.set_values(lwaftr_child,"out-ipv4-frag-not",
                                                self.lwaftr_v4_out_ipv4_frag_not, self.lwaftr_v4_out_ipv4_frag_not_old,
                                                self.lwaftr_v4_out_ipv4_frag_not_ps, newtime)
                                self.set_values(lwaftr_child,"ingress-packet-drops",
                                                self.lwaftr_ifInDiscards, self.lwaftr_ifInDiscards_old,
                                                self.lwaftr_ifInDiscards_ps, newtime)



        # update the self.previous_poll at the end
        self.previous_poll = newtime
	self.display_monitor()


    def display_monitor(self):
        try:
            os.system('clear')

            ltime = datetime.datetime.now()
            jcs.output(SNABB_V6_TEMPLATE %(ltime
					, self.lwaftr_v6_in_ipv6_packets, self.lwaftr_v6_in_ipv6_packets_ps,
                                         self.lwaftr_v6_in_ipv6_bytes,self.lwaftr_v6_in_ipv6_bytes_ps,
                                         self.lwaftr_v6_out_ipv6_packets, self.lwaftr_v6_out_ipv6_packets_ps,
                                         self.lwaftr_v6_out_ipv6_bytes,self.lwaftr_v6_out_ipv6_bytes_ps,
                                         self.lwaftr_v6_drop_all_ipv6_iface_packets, self.lwaftr_v6_drop_all_ipv6_iface_packets_ps,
                                         self.lwaftr_v6_in_ipv6_frag_reassembled, self.lwaftr_v6_in_ipv6_frag_reassembled_ps,
                                         self.lwaftr_v6_drop_ipv6_frag_invalid_reassembly, self.lwaftr_v6_drop_ipv6_frag_invalid_reassembly_ps,
                                         self.lwaftr_v6_out_ipv6_frag, self.lwaftr_v6_out_ipv6_frag_ps,
                                         self.lwaftr_v6_out_ipv6_frag_not, self.lwaftr_v6_out_ipv6_frag_not_ps))
            jcs.output(SNABB_V4_TEMPLATE %(self.lwaftr_ifInDiscards, self.lwaftr_ifInDiscards_ps,
                                         self.lwaftr_v4_in_ipv4_packets, self.lwaftr_v4_in_ipv4_packets_ps,
                                         self.lwaftr_v4_in_ipv4_bytes,self.lwaftr_v4_in_ipv4_bytes_ps,
                                         self.lwaftr_v4_out_ipv4_packets, self.lwaftr_v4_out_ipv4_packets_ps,
                                         self.lwaftr_v4_out_ipv4_bytes,self.lwaftr_v4_out_ipv4_bytes_ps,
                                         self.lwaftr_v4_drop_all_ipv4_iface_packets, self.lwaftr_v4_drop_all_ipv4_iface_packets_ps,
                                         self.lwaftr_v4_in_ipv4_frag_reassembled, self.lwaftr_v4_in_ipv4_frag_reassembled_ps,
                                         self.lwaftr_v4_drop_ipv4_frag_invalid_reassembly, self.lwaftr_v4_drop_ipv4_frag_invalid_reassembly_ps,
                                         self.lwaftr_v4_out_ipv4_frag, self.lwaftr_v4_out_ipv4_frag_ps,
                                         self.lwaftr_v4_out_ipv4_frag_not, self.lwaftr_v4_out_ipv4_frag_not_ps))

        except Exception as e:
            pass

def Main():
    
    try:
        server = xmlrpclib.ServerProxy('http://127.0.0.1:9191', verbose=False)
    except Exception as e:
        jcs.output("Failed to connect to the JET app %s" %e.message)
        return
    
    lw = lwaftr_stats()
    """
    try:
        global read_list, timeout
        while read_list:
            ready = select.select(read_list, [], [], timeout)[0]
            if not ready:
                lw.monitor(server)
            else:
                exit(0)
    except KeyboardInterrupt:
        pass
    """
    while True:
        lw.monitor(server)
	time.sleep(2)

if __name__=='__main__':
    Main()

