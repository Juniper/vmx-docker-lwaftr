# -*- coding: utf-8 -*-
__author__ = "Amish Anand"
__copyright__ = "Copyright (c) 2015 Juniper Networks, Inc."

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
 breaths                                         %15s    %12.2f

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
	self.ids = [] 
        self.lwaftr = {} 
        self.lwaftr_old = {} 
        self.lwaftr_ps = {} 
        self.lwaftr_ifInDiscards = {}
        self.lwaftr_ifInDiscards_old = {}
        self.lwaftr_ifInDiscards_ps = {}
        self.breaths = {}
        self.breaths_old = {}
        self.breaths_ps = {}
        self.previous_poll = 0

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
	    id = instance.findall("./id")[0].text
	    if id in self.ids:
	        pass
	    else:
		self.ids.append(id)
		self.lwaftr[id] = []
		self.lwaftr_old[id] = []
		self.lwaftr_ps[id]=[]
		self.lwaftr_ifInDiscards[id]= "0"
		self.lwaftr_ifInDiscards_old[id] = "0"
		self.lwaftr_ifInDiscards_ps[id] = 0.0
		self.breaths[id] = "0"
		self.breaths_old[id] = "0"
		self.breaths_ps[id] = 0.0
		for i in range(0,len(self.index_dict)):
		    self.lwaftr[id].append("0")
                    self.lwaftr_old[id].append("0")
                    self.lwaftr_ps[id].append(0.0)
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
                                        self.lwaftr_old[id][self.index_dict[tag]] = 0
                                        self.lwaftr[id][self.index_dict[tag]] = 0
                                        self.lwaftr_ps[id][self.index_dict[tag]] = 0.0
                                    else:
                                        self.lwaftr_old[id][self.index_dict[tag]] = self.lwaftr[id][self.index_dict[tag]]
                                        self.lwaftr[id][self.index_dict[tag]] = lwaftr_child.text.strip()
                                        if self.previous_poll != 0:
                                            delta = float(newtime - self.previous_poll)
                                            nwval = float(int(self.lwaftr[id][self.index_dict[tag]])-int(self.lwaftr_old[id][self.index_dict[tag]]))
                                            nwval = round(nwval,2)
                                            self.lwaftr_ps[id][self.index_dict[tag]] = nwval/delta
                                else:
                                    if tag == "ingress-packet-drops":
                                        if lwaftr_child.text.strip() == "":
                                            self.lwaftr_ifInDiscards_old[id] = self.lwaftr_ifInDiscards[id]
                                            self.lwaftr_ifInDiscards_ps[id] = 0.0
                                        else:
                                            self.lwaftr_ifInDiscards_old[id] = self.lwaftr_ifInDiscards[id]
                                            self.lwaftr_ifInDiscards[id] = lwaftr_child.text.strip()
                                            if self.previous_poll != 0:
                                                delta = float(newtime - self.previous_poll)
                                                nwval = float(int(self.lwaftr_ifInDiscards[id])-int(self.lwaftr_ifInDiscards_old[id]))
                                                nwval = round(nwval,2)
                                                self.lwaftr_ifInDiscards_ps[id] = nwval/delta

                if child_instance.tag == "engine":
                    for engine_child in child_instance:
                        if engine_child.tag == "breaths":
                            if engine_child.text.strip() == "":
                                self.breaths_old[id] = self.breaths[id]
                                self.breaths_ps[id] = 0.0
                            else:
                                self.breaths_old[id] = self.breaths[id]
                                self.breaths[id] = engine_child.text.strip()
                                if self.previous_poll != 0:
                                    delta = float(newtime - self.previous_poll)
                                    nwval = float(int(self.breaths[id])-int(self.breaths_old[id]))
                                    nwval = round(nwval,2)
                                    self.breaths_ps[id] = nwval/delta

                self.display_monitor(id)
	if found == 0:
	    jcs.output("Invalid instance")
	    exit(0)
        # update the self.previous_poll at the end
        self.previous_poll = newtime


    def display_monitor(self,id):
        try:
            os.system('clear')
	    ltime = datetime.datetime.now()
            jcs.output(SNABB_V6_TEMPLATE %(ltime,id,
                       self.lwaftr[id][0], self.lwaftr_ps[id][0],
                       self.lwaftr[id][1], self.lwaftr_ps[id][1],
                       self.lwaftr[id][2], self.lwaftr_ps[id][2],
                       self.lwaftr[id][3], self.lwaftr_ps[id][3],
                       self.lwaftr[id][4], self.lwaftr_ps[id][4],
                       self.lwaftr[id][5], self.lwaftr_ps[id][5],
                       self.lwaftr[id][6], self.lwaftr_ps[id][6],
                       self.lwaftr[id][7], self.lwaftr_ps[id][7],
                       self.lwaftr[id][8], self.lwaftr_ps[id][8]))

            jcs.output(SNABB_V4_TEMPLATE %(self.lwaftr_ifInDiscards[id], self.lwaftr_ifInDiscards_ps[id],
                       self.breaths[id],self.breaths_ps[id],
                       self.lwaftr[id][9], self.lwaftr_ps[id][9],
                       self.lwaftr[id][10], self.lwaftr_ps[id][10],
                       self.lwaftr[id][11], self.lwaftr_ps[id][11],
                       self.lwaftr[id][12], self.lwaftr_ps[id][12],
                       self.lwaftr[id][13], self.lwaftr_ps[id][13],
                       self.lwaftr[id][14], self.lwaftr_ps[id][14],
                       self.lwaftr[id][15], self.lwaftr_ps[id][15],
                       self.lwaftr[id][16], self.lwaftr_ps[id][16],
                       self.lwaftr[id][17], self.lwaftr_ps[id][17]))

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

