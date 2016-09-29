from __future__ import print_function
import jcs
import sys
import argparse
from jnpr.junos import Device
from lxml import etree
from time import time
import os
import xml.etree.ElementTree as ET

host_ip = '10.209.16.147'

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
STATS_CACHE_TIME = 60

class lwaftr_statistics:
    def __init__(self, instance_name, v4_inoctect, v4_inpkts, v4_outoctet, v4_outpkts, v4_octetdrops, v4_pktdrops, v6_inoctect, v6_inpkts, v6_outoctet, v6_outpkts, v6_octetdrops, v6_pktdrops):
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
    

# cli commands
# show lwaftr state
# show lwaftr statistics 
# show lwaftr statistics id <>
def populate_stats():
    try:
        jcs.syslog("external.info", "populate statistics")
        
        #hard coding for testing            
        jcs.syslog("external.info", "Filling dummy values for test")

        lwaftr1 = lwaftr_statistics("lwaftr1", 11,12,13,14,15,16, 21,22,23,24,25,26)
        lwaftr_statistics_dict[1] = lwaftr1

        lwaftr2 = lwaftr_statistics("lwaftr2", 31,32,33,34,35,36, 41,42,43,44,45,46)
        lwaftr_statistics_dict[4] = lwaftr2

        lwaftr3 = lwaftr_statistics("lwaftr3", 51,52,53,54,55,56, 61,62,63,64,65,66)
        lwaftr_statistics_dict[8] = lwaftr3
        """
        current_time = time()    
        file_time = 0
        try:
            stat = os.stat(snmp_state_file)
            file_time = stat.st_mtime
        except OSError, e:
            refresh_file = 1

        message = "Timing " + str(file_time) + " " + str(current_time)
        jcs.syslog("external.info", message)

        refresh_file = 1
        if (current_time > file_time and ((current_time - file_time) < STATS_CACHE_TIME)):
            refresh_file = 0

        if (refresh_file == 1): 
            dev = Device(host=host_ip, user='root', password='Embe1mpls')
            dev.open()
            state_rsp =  dev.rpc.get_lwaftr_state()
            state_fp = open(snmp_state_file, "w")
            state_fp.write(etree.tostring(state_rsp))

            statistics_rsp =  dev.rpc.get_lwaftr_statistics()
            statistics_fp = open(snmp_statistics_file, "w")
            statistics_fp.write(etree.tostring(statistics_rsp))
        
            jcs.syslog("external.info", "RPC Invoke complete")
            #jcs.syslog("external.info", etree.tostring(statistics_rsp))
            dev.close()
        else:
            state_rsp = ET.parse(snmp_state_file)
            statistics_rsp = ET.parse(snmp_statistics_file)
            jcs.syslog("external.info", "Using file caching")

        for elem in state_rsp.iter('instance'):
            instance_name = elem.find('id').text.strip()
            instance_id = elem.find('pid').text.strip()
            instance_id = long(instance_id)
            lwaftr_instance_dict[instance_name] = instance_id

        for elem in statistics_rsp.iter('statistics'):
            lwaftrName = elem.find('id').text.strip()
            message = "Instance name: " + lwaftrName
            jcs.syslog("external.info", message)
            lwaftrV4HCInOctets = elem.find('in-ipv4-bytes').text.strip()
            message = "in-ipv4-bytes: " + lwaftrV4HCInOctets
            jcs.syslog("external.info", message)
            lwaftrV4HCInOctets = long(lwaftrV4HCInOctets)

            lwaftrV4HCInPkts = elem.find('in-ipv4-packets').text.strip()
            lwaftrV4HCInPkts = long(lwaftrV4HCInPkts)

            lwaftrV4HCOutOctets = elem.find('out-ipv4-bytes').text.strip()
            lwaftrV4HCOutOctets = long(lwaftrV4HCOutOctets)

            lwaftrV4HCOutPkts = elem.find('out-ipv4-packets').text.strip()
            lwaftrV4HCOutPkts = long(lwaftrV4HCOutPkts)

            lwaftrV4HCOctetDrops = elem.find('drop-all-ipv4-iface-bytes').text.strip()
            lwaftrV4HCOctetDrops = long(lwaftrV4HCOctetDrops)

            lwaftrV4HCPktDrops = elem.find('drop-all-ipv4-iface-packets').text.strip()
            message = "drop-all-ipv4-iface-packets: " + lwaftrV4HCPktDrops
            jcs.syslog("external.info", message)
            lwaftrV4HCPktDrops = long(lwaftrV4HCPktDrops)
            
            lwaftrV6HCInOctets = elem.find('in-ipv6-bytes').text.strip()
            lwaftrV6HCInOctets = long(lwaftrV6HCInOctets)

            lwaftrV6HCInPkts = elem.find('in-ipv6-packets').text.strip()
            lwaftrV6HCInPkts = long(lwaftrV6HCInPkts)

            lwaftrV6HCOutOctets = elem.find('out-ipv6-bytes').text.strip()
            lwaftrV6HCOutOctets = long(lwaftrV6HCOutOctets)

            lwaftrV6HCOutPkts = elem.find('out-ipv6-packets').text.strip()
            lwaftrV6HCOutPkts = long(lwaftrV6HCOutPkts)

            lwaftrV6HCOctetDrops = elem.find('drop-all-ipv6-iface-bytes').text.strip()
            lwaftrV6HCOctetDrops = long(lwaftrV6HCOctetDrops)

            lwaftrV6HCPktDrops = elem.find('drop-all-ipv6-iface-packets').text.strip()
            message = "drop-all-ipv6-iface-packets: " + lwaftrV6HCPktDrops
            jcs.syslog("external.info", message)
            lwaftrV6HCPktDrops = long(lwaftrV6HCPktDrops)

            lwaftr = lwaftr_statistics(lwaftrName, lwaftrV4HCInOctets,lwaftrV4HCInPkts,lwaftrV4HCOutOctets,lwaftrV4HCOutPkts,lwaftrV4HCOctetDrops,lwaftrV4HCPktDrops, 
                        lwaftrV6HCInOctets,lwaftrV6HCInPkts,lwaftrV6HCOutOctets,lwaftrV6HCOutPkts,lwaftrV6HCOctetDrops,lwaftrV6HCPktDrops)
            instance = lwaftr_instance_dict[lwaftrName]
            lwaftr_statistics_dict[instance] = lwaftr
     

        jcs.syslog("external.info", "Device open success")
        """
        
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
        if (leaf == 4):
            jcs.syslog("external.info", "leaf=4")
            value = lwaftr.lwaftrV4HCInOctets
        elif (leaf == 5):
            value = lwaftr.lwaftrV4HCInPkts
        elif (leaf == 6):
            value = lwaftr.lwaftrV4HCOutOctets
        elif (leaf == 7):
            value = lwaftr.lwaftrV4HCOutPkts
        elif (leaf == 8):
            value = lwaftr.lwaftrV4HCOctetDrops
        elif (leaf == 9):
            value = lwaftr.lwaftrV4HCPktDrops
        else:
            return
        return str(value)
    elif (protocol == SNMP_V6_STATISTICS):
        if (leaf == 4):
            value = lwaftr.lwaftrV6HCInOctets
        elif (leaf == 5):
            value = lwaftr.lwaftrV6HCInPkts
        elif (leaf == 6):
            value = lwaftr.lwaftrV6HCOutOctets
        elif (leaf == 7):
            value = lwaftr.lwaftrV6HCOutPkts
        elif (leaf == 8):
            value = lwaftr.lwaftrV6HCOctetDrops
        elif (leaf == 9):
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
            leaf = 3  
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
            if (leaf < 9):
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
        if (leaf == 3):
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
        if (recv_leaf == 3):            
            return jcs.emit_snmp_attributes(oid_name, "string", value)
        else:
            return jcs.emit_snmp_attributes(oid_name, "Integer64", value)
            
    return 
if __name__ == '__main__':
    #populate_stats()
    #print(lwaftr_statistics_dict)
    main()


