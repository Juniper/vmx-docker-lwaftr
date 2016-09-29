from __future__ import print_function
import jcs
import sys
import argparse
from jnpr.junos import Device
from lxml import etree
from time import time
import os
import xml.etree.ElementTree as ET
import xmlrpclib

host_ip = '172.17.0.101'

lw4overmib_table_oid = ".1.3.6.1.4.1.2636.1.7.151.1.1"

snmp_state_file = "/var/tmp/snmp_state.log"
snmp_statistics_file = "/var/tmp/snmp_statistics.log"

lwaftr_statistics_dict = dict()
lwaftr_instance_dict = dict()

SNMP_GET = 1
SNMP_GETNEXT = 2

SNMP_V4_STATISTICS = 1
SNMP_V6_STATISTICS = 2

# 60 sec caching
STATS_CACHE_TIME = 0

# Leaf/members
LWAFTR_INSTANCENAME = 3
LWAFTR_HCINOCTETS = 4
LWAFTR_HCINPACKETS = 5
LWAFTR_HCOUTOCTETS = 6
LWAFTR_HCOUTPACKETS = 7
LWAFTR_HCOCTETDROPS = 8
LWAFTR_HCOPACKETDROPS = 9

class lwaftr_statistics:
    def __init__(self, instance_name, v4_inoctect = 0, v4_inpkts = 0, v4_outoctet = 0, v4_outpkts = 0, v4_octetdrops = 0, v4_pktdrops = 0, 
            v6_inoctect = 0, v6_inpkts = 0, v6_outoctet = 0, v6_outpkts = 0, v6_octetdrops = 0, v6_pktdrops = 0):
        self.lwaftrName = instance_name
        self.lwaftrV4HCInOctets = v4_inoctect
        self.lwaftrV4HCInPkts = v4_inpkts
        self.lwaftrV4HCOutOctets = v4_outoctet
        self.lwaftrV4HCOutPkts = v4_outpkts
        self.lwaftrV4HCOctetDrops = v4_octetdrops
        self.lwaftrV4HCPktDrops = v4_pktdrops

        self.lwaftrV6HCInOctets = v6_inoctect
        self.lwaftrV6HCInPkts = v6_inpkts
        self.lwaftrV6HCOutOctets = v6_outoctet
        self.lwaftrV6HCOutPkts = v6_outpkts
        self.lwaftrV6HCOctetDrops = v6_octetdrops
        self.lwaftrV6HCPktDrops = v6_pktdrops   

    def set_v4stat_value(self, leaf, value):
        if (leaf == LWAFTR_HCINOCTETS):
            self.lwaftrV4HCInOctets = value
        elif (leaf == LWAFTR_HCINPACKETS):
            self.lwaftrV4HCInPkts = value
        elif (leaf == LWAFTR_HCOUTOCTETS):
            self.lwaftrV4HCOutOctets = value
        elif (leaf == LWAFTR_HCOUTPACKETS):
            self.lwaftrV4HCOutPkts = value
        elif (leaf == LWAFTR_HCOCTETDROPS):
            self.lwaftrV4HCOctetDrops = value
        elif (leaf == LWAFTR_HCOPACKETDROPS):
            self.lwaftrV4HCPktDrops = value
            
    def set_v6stat_value(self, leaf, value):
        if (leaf == LWAFTR_HCINOCTETS):
            self.lwaftrV6HCInOctets = value
        elif (leaf == LWAFTR_HCINPACKETS):
            self.lwaftrV6HCInPkts = value
        elif (leaf == LWAFTR_HCOUTOCTETS):
            self.lwaftrV6HCOutOctets = value
        elif (leaf == LWAFTR_HCOUTPACKETS):
            self.lwaftrV6HCOutPkts = value
        elif (leaf == LWAFTR_HCOCTETDROPS):
            self.lwaftrV6HCOctetDrops = value
        elif (leaf == LWAFTR_HCOPACKETDROPS):
            self.lwaftrV6HCPktDrops = value


    
def populate_node_value(elem, tag):
    if (elem.tag == tag):
        value = elem.text.strip()
        message = tag + ": " + value
        jcs.syslog("external.info", message)
        value = long(value)
        return value
    return -1

# cli commands
# show lwaftr state
# show lwaftr statistics 
# show lwaftr statistics id <>
def populate_stats():
    try:
        jcs.syslog("external.info", "populate statistics")
        
        """     
        #hard coding for testing            
        jcs.syslog("external.info", "Filling dummy values for test")

        lwaftr1 = lwaftr_statistics("lwaftr1", 11,12,13,14,15,16, 21,22,23,24,25,26)
        lwaftr_statistics_dict[548] = lwaftr1

        lwaftr2 = lwaftr_statistics("lwaftr2", 31,32,33,34,35,36, 41,42,43,44,45,46)
        lwaftr_statistics_dict[549] = lwaftr2

        lwaftr3 = lwaftr_statistics("lwaftr3", 51,52,53,54,55,56, 61,62,63,64,65,66)
        lwaftr_statistics_dict[550] = lwaftr3
        """

        jcs.syslog("external.info", "Opening Device connection")
        server =  xmlrpclib.ServerProxy('http://127.0.0.1:9191', verbose=False)
        state_rsp = server.lwaftr()
        jcs.syslog("external.info", state_rsp)
        state_rsp = ET.fromstring(state_rsp)

        jcs.syslog("external.info", "RPC Invoke complete")

        root = state_rsp
       
        for state_rsp in root:
          instance_name = None
          instance_id = None
          for instance in state_rsp:
            jcs.syslog("external.info", instance.tag)
            if (instance.tag == 'id'):
                instance_name = instance.text.strip()
            if (instance.tag == 'pid'):
                instance_id = instance.text.strip()
            if (instance_name and instance_id):
                instance_id = long(instance_id)
                lwaftr_instance_dict[instance_name] = instance_id
                message = "Adding instance: " + instance_name
                jcs.syslog("external.info", message)
                lwaftr_entry = lwaftr_statistics(instance_name)
                instance_id = None
            if (instance.tag == 'apps'):
                for child in instance:
                    if (child.tag == 'lwaftr'):
                        message = "Instance name: " + instance_name
                        jcs.syslog("external.info", message)
                        for elem in child:
                            #jcs.syslog("external.info", elem.tag)
                            value = populate_node_value(elem, 'in-ipv4-bytes')
                            if (value >= 0):
                                jcs.syslog("external.info", "Inside filling")
                                lwaftr_entry.set_v4stat_value(LWAFTR_HCINOCTETS, value)
                                continue
                            value = populate_node_value(elem, 'in-ipv4-packets')
                            if (value >= 0):
                                lwaftr_entry.set_v4stat_value(LWAFTR_HCINPACKETS, value)                                
                                continue
                            value = populate_node_value(elem, 'out-ipv4-bytes')
                            if (value >= 0):
                                lwaftr_entry.set_v4stat_value(LWAFTR_HCOUTOCTETS, value)                                
                                jcs.syslog("external.info", "Inside filling")
                                continue
                            value = populate_node_value(elem, 'out-ipv4-packets')
                            if (value >= 0):
                                lwaftr_entry.set_v4stat_value(LWAFTR_HCOUTPACKETS, value)
                                continue                                
                            value = populate_node_value(elem, 'drop-all-ipv4-iface-bytes')
                            if (value >= 0):
                                lwaftr_entry.set_v4stat_value(LWAFTR_HCOCTETDROPS, value)                                                       
                                continue                              
                            value = populate_node_value(elem, 'drop-all-ipv4-iface-packets')
                            if (value >= 0):
                                lwaftr_entry.set_v4stat_value(LWAFTR_HCOPACKETDROPS, value)                                                                                 
                                continue                                
                            value = populate_node_value(elem, 'in-ipv6-bytes')
                            if (value >= 0):
                                lwaftr_entry.set_v6stat_value(LWAFTR_HCINOCTETS, value)                                                                                                             
                                continue                        
                            value = populate_node_value(elem, 'in-ipv6-packets')
                            if (value >= 0):
                                lwaftr_entry.set_v6stat_value(LWAFTR_HCINPACKETS, value)    
                                continue                        
                            value = populate_node_value(elem, 'out-ipv6-bytes')
                            if (value >= 0):
                                lwaftr_entry.set_v6stat_value(LWAFTR_HCOUTOCTETS, value)                                
                                continue                        
                            value = populate_node_value(elem, 'out-ipv6-packets')
                            if (value >= 0):
                                lwaftr_entry.set_v6stat_value(LWAFTR_HCOUTPACKETS, value)   
                                continue                                
                            value = populate_node_value(elem, 'drop-all-ipv6-iface-bytes')
                            if (value >= 0):
                                lwaftr_entry.set_v6stat_value(LWAFTR_HCOCTETDROPS, value)                               
                                continue
                            value = populate_node_value(elem, 'drop-all-ipv6-iface-packets')
                            if (value >= 0):
                                lwaftr_entry.set_v6stat_value(LWAFTR_HCOPACKETDROPS, value)                             
                                continue
                               
                        instance = lwaftr_instance_dict[instance_name]
                        lwaftr_statistics_dict[instance] = lwaftr_entry
     
                        message = "Added an entry: " + instance_name 
                        jcs.syslog("external.info", message)
        
         
    except Exception as err:
        jcs.syslog("external.info", str(err))
        jcs.emit_error("Uncaught esception: {0}".format(err))
        
def snmp_get_value(leaf, instance, protocol):
    message = "Inside snmp_get_value " + "instance: " + str(instance) + " protocol: " + str(protocol)
    jcs.syslog("external.info", message)
    lwaftr = lwaftr_statistics_dict[instance]
    #jcs.syslog("external.info", lwaftr)
    if lwaftr is None:
        jcs.syslog("external.info", "no entry")
        return None
    if (leaf == 3):
        return lwaftr.lwaftrName;
       
    if (protocol == SNMP_V4_STATISTICS):
        if (leaf == LWAFTR_HCINOCTETS):
            jcs.syslog("external.info", "leaf=4")
            value = lwaftr.lwaftrV4HCInOctets
        elif (leaf == LWAFTR_HCINPACKETS):
            value = lwaftr.lwaftrV4HCInPkts
        elif (leaf == LWAFTR_HCOUTOCTETS):
            value = lwaftr.lwaftrV4HCOutOctets
        elif (leaf == LWAFTR_HCOUTPACKETS):
            value = lwaftr.lwaftrV4HCOutPkts
        elif (leaf == LWAFTR_HCOCTETDROPS):
            value = lwaftr.lwaftrV4HCOctetDrops
        elif (leaf == LWAFTR_HCOPACKETDROPS):
            value = lwaftr.lwaftrV4HCPktDrops
        else:
            return
        return str(value)
    elif (protocol == SNMP_V6_STATISTICS):
        if (leaf == LWAFTR_HCINOCTETS):
            value = lwaftr.lwaftrV6HCInOctets
        elif (leaf == LWAFTR_HCINPACKETS):
            value = lwaftr.lwaftrV6HCInPkts
        elif (leaf == LWAFTR_HCOUTOCTETS):
            value = lwaftr.lwaftrV6HCOutOctets
        elif (leaf == LWAFTR_HCOUTPACKETS):
            value = lwaftr.lwaftrV6HCOutPkts
        elif (leaf == LWAFTR_HCOCTETDROPS):
            value = lwaftr.lwaftrV6HCOctetDrops
        elif (leaf == LWAFTR_HCOPACKETDROPS):
            value = lwaftr.lwaftrV6HCPktDrops    
        else:
            return
        return str(value)
    return None
    
def get_next_instance(instance):
    if (instance is None):
        jcs.syslog("external.info", "Inside get_next_instance input null")
    else:
        jcs.syslog("external.info", "Inside get_next_instance input not null")
    found = 0
    for key in sorted(lwaftr_statistics_dict):      
        if (instance is None): 
            message = "Returning instance: " + str(key)
            jcs.syslog("external.info", message)
            return key
        if (key > instance):
            return key 
    if (key):
        message = "Returning instance: " + str(key)
        jcs.syslog("external.info", message)
    return None

    jcs.syslog("external.info", "Returning null")
    return None
    
def snmp_getnext_value(leaf, instance, protocol):
    jcs.syslog("external.info", "Inside snmp_getnext_value ")
    #entry = lwaftr_statistics_dict[instance]
    if (instance is None):
        instance = get_next_instance(instance)
        if (instance is None):
            return None
        if (protocol is None):
            protocol = SNMP_V4_STATISTICS
        if (leaf is None):
            leaf = LWAFTR_INSTANCENAME  
    elif (instance not in lwaftr_statistics_dict):
        jcs.syslog("external.info", "entry is null ")
        instance = get_next_instance(instance)
        if (instance is None):
            return None
        if (protocol < SNMP_V4_STATISTICS and protocol > SNMP_V6_STATISTICS):
            protocol = SNMP_V4_STATISTICS
    elif (protocol < SNMP_V4_STATISTICS):
        protocol = SNMP_V4_STATISTICS
    elif (protocol == SNMP_V4_STATISTICS):
        protocol = SNMP_V6_STATISTICS
    elif (protocol >= SNMP_V6_STATISTICS):
        protocol = SNMP_V4_STATISTICS
        instance = get_next_instance(instance)
        if (instance == None):
            instance = get_next_instance(None)
            if (instance is None):
                return None
            if (leaf < LWAFTR_HCOPACKETDROPS):
                leaf = leaf + 1
            else:
                return None
    value = snmp_get_value(leaf, instance, protocol)
    if (value is None):
        return (None, None, None, None)
    message = "Inside snmp_getnext_value " + value
    jcs.syslog("external.info", message)
    message = "(" + str(leaf) + " " + str(instance) + " " + str(protocol) + " " + str(value) + ")"
    jcs.syslog("external.info", message)
    return (leaf, instance, protocol, value)
    
def main():
    snmp_action = jcs.get_snmp_action()
    snmp_oid = jcs.get_snmp_oid()

    #jcs.enable_debugger()
    # invoke lwaftr stats
    populate_stats()

    # log operation, oid
    message = "snmp_action: "
    message += snmp_action
    message += ", oid: "
    message += snmp_oid
    jcs.syslog("external.info", message)


    """
    if (lwaftr_statistics_dict.size() == 0):
        #fill null
        #return jcs.emit_snmp_attributes(snmp_oid, None, None)
        return
    """
    if (snmp_action == "get"):
        operation = SNMP_GET
    elif (snmp_action == "get-next"):
        operation = SNMP_GETNEXT
        
    oid_list = snmp_oid.split(".")  
    oid_list_len = len(oid_list)

    leaf = None
    instance_id = None
    protocol = None
    if (oid_list_len > 13):
        leaf = oid_list[13]
        leaf = int(leaf)

    message = "Leaf value " + str(leaf)
    jcs.syslog("external.info", message)

    if (oid_list_len > 14):
        instance_id = oid_list[14]
        instance_id = int(instance_id)

    if (oid_list_len > 15):
        protocol = oid_list[15]
        protocol = int(protocol)

    message = "Parameters "
    if (leaf):
        message += "leaf: " + str(leaf)
    if (instance_id):
        message += " instance_id: " + str(instance_id)
    if (protocol):
        message += " protocol: " + str(protocol)
    jcs.syslog("external.info", message)
    
    if (operation == SNMP_GET):
        jcs.syslog("external.info", "get request")
        value = snmp_get_value(leaf, instance_id, protocol)
        if (value is None):
            jcs.syslog("external.info", "No entry available") 
        return
        value = str(value)
        message = "value: " + value
        if (leaf == LWAFTR_INSTANCENAME):
            message = message + " " + snmp_oid
            jcs.syslog("external.info", message) 
            return jcs.emit_snmp_attributes(snmp_oid, "string", value)
        else:
            return jcs.emit_snmp_attributes(snmp_oid, "Counter64", value)
    elif (operation == SNMP_GETNEXT):
        (recv_leaf, recv_instance, recv_protocol, value) = snmp_getnext_value(leaf, instance_id, protocol)
        if (value is None):
            jcs.syslog("external.info", "No entry available") 
            return None;
        else:
            jcs.syslog("external.info", value) 
        message = "Returning OID name: "
        oid_name = lw4overmib_table_oid + "." + str(recv_leaf) + "." + str(recv_instance) + "." + str(recv_protocol)
        message += oid_name
        jcs.syslog("external.info", message) 
        if (recv_leaf == LWAFTR_INSTANCENAME):            
            return jcs.emit_snmp_attributes(oid_name, "string", value)
        else:
            return jcs.emit_snmp_attributes(oid_name, "Integer64", value)
            
    return 
if __name__ == '__main__':
    main()



