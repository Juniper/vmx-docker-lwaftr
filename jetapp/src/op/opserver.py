__author__ = "Amish Anand"
__copyright__ = "Copyright (c) 2015 Juniper Networks, Inc."

import os
from twisted.web import xmlrpc

from utils.jetapplog import LOG
import subprocess
import tempfile
from opglobals import *

# Need to add logic of reading the parameters from the filesystem
class OpServer(xmlrpc.XMLRPC):

    def read_snabb_counter(self,complete_name):
        # Returns the integer for the requested counter
        # Check if the file exists
        if not os.path.isfile(complete_name):
            print('File %s not found' %complete_name)
            raise IOError('File %s not found' %complete_name)
        infile = open(complete_name,"rb")
        line_len = 8
        byte_addr = 0
        cnt = 0
        buf = infile.read(line_len)
        hex_num = ''
        while cnt < 8:
            byte_addr += len(buf)
            for c in buf:
                hex_num = '{:>02s}'.format((hex(ord(c))[2:].upper())) + hex_num
            buf = infile.read(line_len)
            cnt += 1
        infile.close()
        int_num = int(hex_num,16)
        return int_num

    """
    This api will find all the pids of snabb instances and parse the specific info
    """
    def get_pid_from_instance_id(self, instance_id):
        idinfo = []
        if instance_id == None:
            pattern = r'"id xe"'
        else:
            pattern = r'"id xe'+str(instance_id) + r'"'
        cmd = r"ps ax | grep " + pattern + r" | grep -v grep"
        output = subprocess.check_output(cmd, shell=True)
        if not output:
            LOG.info('No Snabb instances are running')
            return None
        id_specific_attributes = {}
        LOG.info('The pids of all instances is %s' %(output.replace('\n',' ')))
        for items in output.split('\n')[:-1]:
            id_specific_attributes['pid'] = items.split(' ')[2]
            id_specific_attributes['id'] = items.split(' ')[-7]
            id_specific_attributes['pci'] = items.split(' ')[-5]
            id_specific_attributes['mac'] = items.split(' ')[-3]
            idinfo.append(id_specific_attributes)
            id_specific_attributes = {}
        return idinfo

    def lwaftr_v4(self, instance_pid):
        """
        :return: Returns the v4 received counters
        """
        LOG.info("Called to fetch lwaftr_v4 stats for pid: %s" %instance_pid)
        # Assuming that the caller has sent pid and not just the instance id
        path = SNABB_COUNTER_BASE_PATH + str(instance_pid)+ r'/lwaftr_v4/'
        rc_dict = {}
        dirs = os.listdir(path)
        for files in dirs:
            counter_name = path+str(files)
            rc_dict[str(files)] = str(self.read_snabb_counter(counter_name))
        return rc_dict

    def lwaftr_v6(self, instance_pid):
        LOG.info("Called to fetch lwaftr_v6 stats for pid: %s" %instance_pid)
        # Assuming that the caller has sent pid and not just the instance id
        path = SNABB_COUNTER_BASE_PATH + str(instance_pid)+ r'/lwaftr_v6/'
        rc_dict = {}
        dirs = os.listdir(path)
        for files in dirs:
            counter_name = path+str(files)
            rc_dict[str(files)] = str(self.read_snabb_counter(counter_name))
        print rc_dict
        return rc_dict

    def lwaftr_thruput_v4(self, instance_pid):
        LOG.info("Called to fetch thruput parameters for pid: %s" %instance_pid)
        path = SNABB_COUNTER_BASE_PATH + str(instance_pid)+ r'/counters/lwaftr.v4 -> nh_fwd4.service/'
        rc_dict = {}
        dirs = os.listdir(path)
        for files in dirs:
            counter_name = path+str(files)
            dict_entry_name = r"lwaftr_v4" + str(files)
            rc_dict[dict_entry_name] = str(self.read_snabb_counter(counter_name))
        print rc_dict
        return rc_dict


    def lwaftr_thruput_v6(self, instance_pid):
        LOG.info("Called to fetch thruput parameters for pid: %s" %instance_pid)
        path = SNABB_COUNTER_BASE_PATH + str(instance_pid)+ r'/counters/lwaftr.v6 -> nh_fwd6.service/'
        rc_dict = {}
        dirs = os.listdir(path)
        for files in dirs:
            counter_name = path+str(files)
            dict_entry_name = r"lwaftr_v6" + str(files)
            rc_dict[dict_entry_name] = str(self.read_snabb_counter(counter_name))
        print rc_dict
        return rc_dict

    def lwaftr_nic(self, instance_pid):
        LOG.info("Called to fetch nic stats for pid: %s" %instance_pid)
        path = SNABB_COUNTER_BASE_PATH + str(instance_pid)+ r'/nic/'
        rc_dict = {}
        dirs = os.listdir(path)
        for files in dirs:
            counter_name = path+str(files)
            dict_entry_name = str(files)
            rc_dict[dict_entry_name] = str(self.read_snabb_counter(counter_name))
        print rc_dict
        return rc_dict

    """
    This RPC will return all the lwaftr counters for all or requested instance
    """
    def xmlrpc_lwaftr(self, instance_id=None):
        complete_response = []
        response_dict = {}
        instance_info = self.get_pid_from_instance_id(instance_id)
        if instance_info == None:
            LOG.info('Could not fetch any snabb counters')
            return 0
        for items in instance_info:
            print "Iteration : " , items
            id = items['pid']
            lwaftr_v4 = self.lwaftr_v4(id)
            lwaftr_v6 = self.lwaftr_v6(id)
            response_dict['lwaftr_v4'] = lwaftr_v4
            response_dict['lwaftr_v6'] = lwaftr_v6
            lwaftr_v4_thruput = self.lwaftr_thruput_v4(id)
            lwaftr_v6_thruput = self.lwaftr_thruput_v6(id)
            response_dict['lwaftr_v4_thruput'] = lwaftr_v4_thruput
            response_dict['lwaftr_v6_thruput'] = lwaftr_v6_thruput
            response_dict['instance_attribute'] = items
            nic = self.lwaftr_nic(id)
            response_dict['nic'] = nic
            complete_response.append(response_dict)
            response_dict = {}
            lwaftr_v4 = {}
            lwaftr_v6 = {}
        return complete_response


    """
    This RPC will return the list of instances running on the host
    """
    def xmlrpc_snabb_instances(self):
        LOG.info("Called")
        complete_response = []
        response_dict = {}
        instance_info = self.get_pid_from_instance_id(None)
        if instance_info == None:
            LOG.info('Could not fetch any snabb counters')
            return 0
        for items in instance_info:
            response_dict['instance_attribute'] = items
            complete_response.append(response_dict)
            response_dict = {}
        return complete_response
