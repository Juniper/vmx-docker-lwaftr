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
Instance ID: %s
                                                           Total      per second
 lwaftr_v6 in-ipv6-packets                       %15s    %12.2f
 lwaftr_v6 in-ipv6-bytes                         %15s    %12.2f
 lwaftr_v6 out-ipv6-packets                      %15s    %12.2f
 lwaftr_v6 out-ipv6-bytes                        %15s    %12.2f
 lwaftr_v6 drop-all-ipv6-iface-packets           %15s    %12.2f
 lwaftr_v6 in-ipv6-frag-reassembled              %15s    %12.2f
 lwaftr_v6 drop-ipv6-frag-invalid-reassembly     %15s    %12.2f
 lwaftr_v6 out-ipv6-frag                         %15s    %12.2f
 lwaftr_v6 out-ipv6-frag-not                     %15s    %12.2f

"""
SNABB_V4_TEMPLATE = r"""
                                                           Total      per second
 nic ifInDiscards                                %15s    %12.2f

                                                           Total      per second
 lwaftr_v4 in-ipv4-packets                       %15s    %12.2f
 lwaftr_v4 in-ipv4-bytes                         %15s    %12.2f
 lwaftr_v4 out-ipv4-packets                      %15s    %12.2f
 lwaftr_v4 out-ipv4-bytes                        %15s    %12.2f
 lwaftr_v4 drop-all-ipv4-iface-packets           %15s    %12.2f
 lwaftr_v4 in-ipv4-frag-reassembled              %15s    %12.2f
 lwaftr_v4 drop-ipv4-frag-invalid-reassembly     %15s    %12.2f
 lwaftr_v4 out-ipv4-frag                         %15s    %12.2f
 lwaftr_v4 out-ipv4-frag-not                     %15s    %12.2f
 """

class lwaftr_stats:
    def __init__(self):
        self.lwaftr_v4_rx = "0.00"
        self.lwaftr_v4_tx = "0.00"
        self.lwaftr_v4_txdrop = "0.00"
        self.lwaftr_v6_rx = "0.00"
        self.lwaftr_v6_tx = "0.00"
        self.lwaftr_v6_txdrop = "0.00"
	self.id = "0"

        #Index array that will be used in the modifier
        self.index_dict = {
            "in-ipv6-packets"                   : 0,
            "in-ipv6-bytes"                     : 1,
            "out-ipv6-packets"                  : 2,
            "out-ipv6-bytes"                    : 3,
            "drop-all-ipv6-iface-packets"       : 4,
            "in-ipv6-frag-reassembled"          : 5,
            "drop-ipv6-frag-invalid-reassembly" : 6,
            "out-ipv6-frag"                     : 7,
            "out-ipv6-frag-not"                 : 8,
            "in-ipv4-packets"                   : 9,
            "in-ipv4-bytes"                     : 10,
            "out-ipv4-packets"                  : 11,
            "out-ipv4-bytes"                    : 12,
            "drop-all-ipv4-iface-packets"       : 13,
            "in-ipv4-frag-reassembled"          : 14,
            "drop-ipv4-frag-invalid-reassembly" : 15,
            "out-ipv4-frag"                     : 16,
            "out-ipv4-frag-not"                 : 17
        }
        #lwaftr cumulative counters
        self.lwaftr = []
        #lwaftr old cumulative counters
        self.lwaftr_old = []
        #lwaftr persec counters
        self.lwaftr_ps = []
        #nic counters
        self.lwaftr_ifInDiscards = "0"
        self.lwaftr_ifInDiscards_old = "0"
        self.lwaftr_ifInDiscards_ps = 0.0
        self.previous_poll = 0

        for i in range(0,len(self.index_dict)):
            self.lwaftr.append("0")
            self.lwaftr_old.append("0")
            self.lwaftr_ps.append(0.0)

    def monitor(self, server, argv):
        try:
            newstats = server.lwaftr()
        except Exception as e:
            jcs.output("%s" %e.message)
            exit(0)
        # newstats contains all the latest stats
        instance_id = ""
        for i in range(0,len(argv)):
            if argv[i] == "id":
                instance_id = argv[i+1]
                break
        newtime = time.time()
        root = ET.fromstring(newstats)
	found = 0
        for instance in root:
	  if instance_id != "" and instance.findall("./id")[0].text != argv[2]:
	    pass
	  else:
	    self.id = instance.findall("./id")[0].text
	    found = 1
            for child_instance in instance:
                if child_instance.tag == "apps":
                    for app_child in child_instance:
                        if app_child.tag == "lwaftr":
                            for lwaftr_child in app_child:
                                tag = lwaftr_child.tag
                                if self.index_dict.has_key(tag):
                                    # set the corresponding counters
                                    if lwaftr_child.text.strip() == "":
                                        # TODO should we just leave it like that?
                                        # as of now i am just updating the old vales to the new one and set ps to 0
                                        self.lwaftr_old[self.index_dict[tag]] = self.lwaftr[self.index_dict[tag]]
                                        self.lwaftr_ps[self.index_dict[tag]] = 0.0
                                    else:
                                        self.lwaftr_old[self.index_dict[tag]] = self.lwaftr[self.index_dict[tag]]
                                        self.lwaftr[self.index_dict[tag]] = lwaftr_child.text.strip()
                                        if self.previous_poll != 0:
                                            delta = float(newtime - self.previous_poll)
                                            nwval = float(int(self.lwaftr[self.index_dict[tag]])-int(self.lwaftr_old[self.index_dict[tag]]))
					    nwval = round(nwval,2)
                                            self.lwaftr_ps[self.index_dict[tag]] = nwval/delta
                                else:
                                    if tag == "ingress-packet-drops":
                                        if lwaftr_child.text.strip() == "":
                                            self.lwaftr_ifInDiscards_old = self.lwaftr_ifInDiscards
                                            self.lwaftr_ifInDiscards_ps = 0.0
                                        else:
                                            self.lwaftr_ifInDiscards_old = self.lwaftr_ifInDiscards
                                            self.lwaftr_ifInDiscards = lwaftr_child.text.strip()
                                            if self.previous_poll != 0:
                                                delta = float(newtime - self.previous_poll)
                                                nwval = float(int(self.lwaftr_ifInDiscards)-int(self.lwaftr_ifInDiscards_old))
					        nwval = round(nwval,2)
                                                self.lwaftr_ifInDiscards_ps = nwval/delta
            self.display_monitor()
	if found == 0:
	    jcs.output("Invalid instance")
	    exit(0)
        # update the self.previous_poll at the end
        self.previous_poll = newtime


    def display_monitor(self):
        try:
            os.system('clear')
	    ltime = datetime.datetime.now()
            jcs.output(SNABB_V6_TEMPLATE %(ltime,self.id,
                       self.lwaftr[0], self.lwaftr_ps[0],
                       self.lwaftr[1], self.lwaftr_ps[1],
                       self.lwaftr[2], self.lwaftr_ps[2],
                       self.lwaftr[3], self.lwaftr_ps[3],
                       self.lwaftr[4], self.lwaftr_ps[4],
                       self.lwaftr[5], self.lwaftr_ps[5],
                       self.lwaftr[6], self.lwaftr_ps[6],
                       self.lwaftr[7], self.lwaftr_ps[7],
                       self.lwaftr[8], self.lwaftr_ps[8]))

            jcs.output(SNABB_V4_TEMPLATE %(self.lwaftr_ifInDiscards, self.lwaftr_ifInDiscards_ps,
                       self.lwaftr[9], self.lwaftr_ps[9],
                       self.lwaftr[10], self.lwaftr_ps[10],
                       self.lwaftr[11], self.lwaftr_ps[1],
                       self.lwaftr[12], self.lwaftr_ps[2],
                       self.lwaftr[13], self.lwaftr_ps[3],
                       self.lwaftr[14], self.lwaftr_ps[4],
                       self.lwaftr[15], self.lwaftr_ps[5],
                       self.lwaftr[16], self.lwaftr_ps[6],
                       self.lwaftr[17], self.lwaftr_ps[17]))

        except Exception as e:
            pass

def Main(argv):
    
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
        lw.monitor(server,argv)
	time.sleep(2)

if __name__=='__main__':
    Main(sys.argv)

