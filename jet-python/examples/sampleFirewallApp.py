#!/usr/bin/env python
#
# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER
#
# Copyright (c) 2015 Juniper Networks, Inc.
# All rights reserved.
#
# Use is subject to license terms.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Sample application file for the testing of Firewall service hosted by the JSD server
Please modify the default parameters described below for proper testing.
Usage:
$python sampleFirewallApp.py --user <username> --password <password> --address <JSD host IP> --port <port number>

"""

import argparse
import logging
import time
import sys
import traceback

# JET shim layer imports
from jnpr.jet.JetHandler import *

# IMPORTANT: Following are the dummy parameters that will be used for testing
# different services. Please change the parameters for proper testing.

# Device Details and Loging Credentials.
DEFAULT_JSD_HOST = 'localhost'
DEFAULT_JSD_PORT = 9090
DEFAULT_JSD_USERNAME = 'foo'
DEFAULT_JSD_PASSWORD = 'bar'

# For SSL based thrift server
DEFAULT_JSD_SSL_CERTIFICATE_PATH = None

# Logging Parameters
DEFAULT_LOG_FILE_NAME = os.path.basename(__file__).split('.')[0]+'.log'
DEFAULT_LOG_LEVEL = logging.DEBUG

# Firewall Testing parameters
# Policer default parameters
DEFAULT_FIREWALL_POLICER_FLAG = AclPolicerFlags.ACL_POLICER_FLAG_TERM_SPECIFIC
DEFAULT_FIREWALL_POLICER_BANDWIDTH = 1000
DEFAULT_FIREWALL_POLICER_BW_UNIT = AclPolicerRate.ACL_POLICER_RATE_BPS
DEFAULT_FIREWALL_POLICER_BURST_SIZE = 1500
DEFAULT_FIREWALL_POLICER_BURST_UNIT = AclPolicerBurstSize.ACL_POLICER_BURST_SIZE_BYTE
DEFAULT_FIREWALL_POLICER_DISCARD = AclBooleanType.ACL_TRUE
DEFAULT_FIREWALL_POLICER_TYPE = AclPolicerType.ACL_TWO_COLOR_POLICER
# Term match default parameters
DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR1 = '1.1.1.1'
DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR1_LEN = 32
DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR1_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR1 = '2.2.2.1'
DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR1_LEN = 32
DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR1_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_DST_PORT1_MIN = 10
DEFAULT_FIREWALL_TERM_MATCH_DST_PORT1_MAX = 11
DEFAULT_FIREWALL_TERM_MATCH_DST_PORT1_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_DST_PORT2_MIN = 20
DEFAULT_FIREWALL_TERM_MATCH_DST_PORT2_MAX = 30
DEFAULT_FIREWALL_TERM_MATCH_DST_PORT2_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT1_MIN = 90
DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT1_MAX = 91
DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT1_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT2_MIN = 80
DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT2_MAX = 81
DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT2_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR2 = '1.1.1.2'
DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR2_LEN = 32
DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR2_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR2 = '2.2.2.2'
DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR2_LEN = 32
DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR2_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL



DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_1_MIN = 1
DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_1_MAX = 1
DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_1_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_2_MIN = 1
DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_2_MAX = 1
DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_2_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_1_MIN = 9
DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_1_MAX = 9
DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_1_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_2_MIN = 10
DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_2_MAX = 12
DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_2_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_1_MIN = 2
DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_1_MAX = 2
DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_1_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_2_MIN = 10
DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_2_MAX = 12
DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_2_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_1_MIN = 3
DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_1_MAX = 3
DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_1_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_2_MIN = 5
DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_2_MAX = 6
DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_2_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_1_MIN = 10
DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_1_MAX = 10
DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_1_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_2_MIN = 11
DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_2_MAX = 12
DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_2_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_TTL_1_MIN = 2
DEFAULT_FIREWALL_TERM_MATCH_TTL_1_MAX = 2
DEFAULT_FIREWALL_TERM_MATCH_TTL_1_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_TTL_2_MIN = 16
DEFAULT_FIREWALL_TERM_MATCH_TTL_2_MAX = 17
DEFAULT_FIREWALL_TERM_MATCH_TTL_2_OP = AclMatchOperation.ACL_MATCH_OP_EQUAL

DEFAULT_FIREWALL_TERM_MATCH_FRAGMENT_TYPES = AclFragmentFlags.ACL_FRAGMENT_NONE
DEFAULT_FIREWALL_TERM_MATCH_PRECEDENCE = Precedence.ACL_PRECEDENCE_CRITICAL_ECP
DEFAULT_FIREWALL_TERM_MATCH_IFL_NAMES = "ge-0/0/1"

# Term default action parameters
DEFAULT_FIREWALL_TERM_ACTION_ACCEPT = AclBooleanType.ACL_TRUE
DEFAULT_FIREWALL_TERM_ACTION_SYSLOG = AclBooleanType.ACL_TRUE
DEFAULT_FIREWALL_TERM_ACTION_LOG = AclBooleanType.ACL_TRUE

# Filter default parameters
DEFAULT_FIREWALL_FILTER_FAMILY = AccessListFamilies.ACL_FAMILY_INET
DEFAULT_FIREWALL_FILTER_TYPES = AccessListTypes.ACL_TYPE_CLASSIC
DEFAULT_FIREWALL_FILTER_BIND_INTERFACE = "ge-0/0/1"
DEFAULT_FIREWALL_FILTER_BIND_DIRECTION = AclBindDirection.ACL_BIND_DIRECTION_INPUT


# Enable Logging to a file
logging.basicConfig(filename=DEFAULT_LOG_FILE_NAME, level=DEFAULT_LOG_LEVEL)

"""
This API will perform all the firewall tests
"""

def FirewallTests(client):
    fw_handle = client.GetFirewallService()
    print '############################################################'
    for x in range(0, 1):
        # Policer Tests
        policer = AccessListPolicer()
        policer.policer_params = AclPolicerParameter()
        policer.policer_params.two_color_parameter = AclPolicerTwoColor()
        policer.policer_params.two_color_parameter.bandwidth = DEFAULT_FIREWALL_POLICER_BANDWIDTH
        policer.policer_params.two_color_parameter.bw_unit = DEFAULT_FIREWALL_POLICER_BW_UNIT
        policer.policer_params.two_color_parameter.burst_size = DEFAULT_FIREWALL_POLICER_BURST_SIZE
        policer.policer_params.two_color_parameter.burst_unit = DEFAULT_FIREWALL_POLICER_BURST_UNIT
        policer.policer_params.two_color_parameter.discard = DEFAULT_FIREWALL_POLICER_DISCARD
        policer.policer_name = "policer1"
        policer.policer_flag = DEFAULT_FIREWALL_POLICER_FLAG
        policer.policer_type = DEFAULT_FIREWALL_POLICER_TYPE

        result = fw_handle.AccessListPolicerAdd(policer)
        print 'Invoking PolicerAdd \nresult = ', result
        policer.policer_params.two_color_parameter.bandwidth = 1000
        policer.policer_params.two_color_parameter.bw_unit = AclPolicerBurstSize.ACL_POLICER_BURST_SIZE_BYTE
        result = fw_handle.AccessListPolicerReplace(policer)
        print 'Invoked AccessListPolicerChange \nresult= ', result

        # ACL tests
        dst1 = AclMatchIpAddress(IpAddress(addr_string=DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR1),
                                 DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR1_LEN,
                                 DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR1_OP)
        dst2 = AclMatchIpAddress(IpAddress(addr_string=DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR2),
				 DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR2_LEN,
                            	 DEFAULT_FIREWALL_TERM_MATCH_DST_ADDR2_OP)
        src1 = AclMatchIpAddress(IpAddress(addr_string=DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR1),
				 DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR1_LEN,
                                 DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR1_OP)
        src2 = AclMatchIpAddress(IpAddress(addr_string=DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR2),
				 DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR2_LEN,
                                 DEFAULT_FIREWALL_TERM_MATCH_SRC_ADDR2_OP)

        dport1 = AclMatchPort(DEFAULT_FIREWALL_TERM_MATCH_DST_PORT1_MIN, DEFAULT_FIREWALL_TERM_MATCH_DST_PORT1_MAX,
                              DEFAULT_FIREWALL_TERM_MATCH_DST_PORT1_OP)
        dport2 = AclMatchPort(DEFAULT_FIREWALL_TERM_MATCH_DST_PORT2_MIN, DEFAULT_FIREWALL_TERM_MATCH_DST_PORT2_MIN,
                              DEFAULT_FIREWALL_TERM_MATCH_DST_PORT2_OP)

        sport1 = AclMatchPort(DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT1_MIN, DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT1_MAX,
                              DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT1_OP)
        sport2 = AclMatchPort(DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT2_MIN, DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT2_MAX,
                              DEFAULT_FIREWALL_TERM_MATCH_SRC_PORT2_OP)

        dscp1 = AclMatchDscpCode(DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_1_MIN,
            DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_1_MAX,
            DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_1_OP)
        dscp2 = AclMatchDscpCode(DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_2_MIN,
            DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_2_MAX,
            DEFAULT_FIREWALL_TERM_MATCH_DSCP_CODE_2_OP)

        protocol1 = AclMatchProtocol(DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_1_MIN, DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_1_MAX,
                                  DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_1_OP)
        protocol2 = AclMatchProtocol(DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_2_MIN, DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_2_MAX,
                                  DEFAULT_FIREWALL_TERM_MATCH_PROTOCOL_2_OP)
        icmp_type1 = AclMatchIcmpType(DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_1_MIN,
                                   DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_1_MAX,
                                   DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_1_OP)
        icmp_type2 = AclMatchIcmpType(DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_2_MIN,
                                   DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_2_MAX,
                                   DEFAULT_FIREWALL_TERM_MATCH_ICMP_TYPE_2_OP)
        icmp_code1 = AclMatchIcmpCode(DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_1_MIN,
                                   DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_1_MAX,
                                   DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_1_OP)
        icmp_code2 = AclMatchIcmpCode(DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_2_MIN,
                                   DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_2_MAX,
                                   DEFAULT_FIREWALL_TERM_MATCH_ICMP_CODE_2_OP)
        pkt_len1 = AclMatchPktLen(DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_1_MIN,
                               DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_1_MAX,
                               DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_1_OP)
        pkt_len2 = AclMatchPktLen(DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_2_MIN,
                               DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_2_MAX,
                               DEFAULT_FIREWALL_TERM_MATCH_PKT_LEN_2_OP)
        ttl1 = AclMatchTtl(DEFAULT_FIREWALL_TERM_MATCH_TTL_1_MIN, DEFAULT_FIREWALL_TERM_MATCH_TTL_1_MAX,
                        DEFAULT_FIREWALL_TERM_MATCH_TTL_1_OP)
        ttl2 = AclMatchTtl(DEFAULT_FIREWALL_TERM_MATCH_TTL_2_MIN, DEFAULT_FIREWALL_TERM_MATCH_TTL_2_MAX,
                        DEFAULT_FIREWALL_TERM_MATCH_TTL_2_OP)

        term1 = AclInetEntry()
        term1.ace_name = "term1"
        term1.ace_op = AclEntryOperation.ACL_ENTRY_OPERATION_ADD

        term1Match1 = AclEntryMatchInet()
        # Create a term object with default parameters
        term1Match1.match_dst_addrs = [dst1,dst2]
        term1Match1.match_src_addrs = [src1, src2]
        term1Match1.match_dst_ports = [dport1, dport2]
        term1Match1.match_src_ports = [sport1, sport2]
        term1Match1.match_dscp_code = [dscp1, dscp2]
        term1Match1.match_protocols = [protocol1, protocol2]
        term1Match1.match_icmp_type = [icmp_type1, icmp_type2]
        term1Match1.match_icmp_code = [icmp_code1, icmp_code2]
        term1Match1.match_pkt_len = [pkt_len1, pkt_len2]
        term1Match1.match_ttl = [ttl1, ttl2]
        term1Match1.fragment_types = DEFAULT_FIREWALL_TERM_MATCH_FRAGMENT_TYPES
        term1Match1.precedences = DEFAULT_FIREWALL_TERM_MATCH_PRECEDENCE

        term1.actions = AclEntryInetAction()
        term1.actions.actions_nt = AclEntryInetNonTerminatingAction()
	term1.actions.action_t = AclEntryInetTerminatingAction()
        term1Action1 = AclEntryInetAction()
        term1Action1NonTerminating = AclEntryInetNonTerminatingAction()
	term1Action1NonTerminating.action_count = AclActionCounter()
	term1Action1NonTerminating.action_count.counter_name = "count1"
	term1.actions.actions_nt = term1Action1NonTerminating
	term1.actions.action_t.action_accept = AclBooleanType.ACL_TRUE 
        term1.matches = term1Match1

        tlist = AclEntry()
	tlist.inet_entry = term1
        filter = AccessList()
        filter.acl_name = "filter1"
        filter.acl_type = DEFAULT_FIREWALL_FILTER_TYPES
        filter.acl_flag = AccessListFlags.ACL_FLAGS_NONE
        filter.acl_family = DEFAULT_FIREWALL_FILTER_FAMILY
        filter.ace_list= []
        filter.ace_list = [tlist]

	# Tests for adding a filter
        result = fw_handle.AccessListAdd(filter)
        print 'Invoking client.AccessListAdd: return = ', result
        raw_input('Added a filter, enter any key to continue ?')

	# Tests for changing a filter
        term2 = AclInetEntry()
        term2.ace_name = "term2"
        term2.ace_op = AclEntryOperation.ACL_ENTRY_OPERATION_ADD
        term2Action1 = AclEntryInetAction()
        term2Action1.action_t = AclEntryInetTerminatingAction()
        term2Action1.action_t.action_discard = AclBooleanType.ACL_TRUE
        term2Action1NonTerminatingActions = AclEntryInetNonTerminatingAction()
        term2Action1NonTerminatingActions.action_count = AclActionCounter("count2")
        term2Action1.actions_nt = AclEntryInetNonTerminatingAction() 
        term2Action1.actions_nt = term2Action1NonTerminatingActions
        term2.actions = AclEntryInetAction() 
        term2.actions = term2Action1
        term2.adjacency = AclAdjacency(AclAdjacencyType.ACL_ADJACENCY_AFTER, 'term1')
        tlist2 = AclEntry()
        tlist2.inet_entry = AclInetEntry()
        tlist2.inet_entry = term2
        filter.ace_list = [tlist2]
	result = fw_handle.AccessListChange(filter)
	print 'Invoking client.AccessListChange to add a new term: return = ', result
	raw_input('Added a filter, enter any key to continue ?')
	term2.ace_op = AclEntryOperation.ACL_ENTRY_OPERATION_DELETE
	tlist2.inet_entry = term2
	filter.ace_list = [tlist2]
        # Now lets put the term1 infront of term2 and replace the existing filter
        result = fw_handle.AccessListChange(filter)
        print 'Invoking client.AccessListChange to delete one of the terms: return = ', result
	raw_input('Added a filter, enter any key to continue ?')

	# Tests to bind the ACL
        bindobj = AccessListObjBind()
        bindobj.acl = filter
        bindobj.obj_type = AccessListBindObjType.ACL_BIND_OBJ_TYPE_INTERFACE
        bindobj.bind_object = DEFAULT_FIREWALL_FILTER_BIND_INTERFACE
        bindobj.bind_direction = DEFAULT_FIREWALL_FILTER_BIND_DIRECTION
        bindobj.bind_family = AccessListFamilies.ACL_FAMILY_INET

        result = fw_handle.AccessListBindAdd(bindobj)
        print 'Invoking AccessListBindAdd: return = ', result
	raw_input('Added a filter, enter any key to continue ?')

	# Tests for filter counters
        aclCounter = AccessListCounter()
        aclCounter.acl = filter
        aclCounter.counter_name = "count1"
        ret = fw_handle.AccessListCounterClear(aclCounter)
        print 'Invoked AccessListCounterClear:\nresult=', ret

        ret = fw_handle.AccessListCounterGet(aclCounter)
        print 'Invoked AccessListCounterGet:\nresult=', ret

        # policerStats = AccessListCounter()
        # policerStats.acl = filter
        # policerStats.policer_name = "policer1"
        # ret = fw_handle.AccessListPolicerCounterStatsGet(policerStats)
        # print 'Invoked AccessListPolicerCounterStatsGet:\nresult= ', ret

        # Unbind the configured filter
        result = fw_handle.AccessListBindDelete(bindobj)
        print 'Invoking AccessListBindDelete: return = ', result

        # Delete the configured filter
        filter = AccessList()
        filter.acl_name = "filter1"
        filter.acl_type = DEFAULT_FIREWALL_FILTER_TYPES
        filter.acl_flag = AccessListFlags.ACL_FLAGS_NONE
        filter.acl_family = DEFAULT_FIREWALL_FILTER_FAMILY

        result = fw_handle.AccessListDelete(filter)
        print 'Invoking client.FilterDelete: return = ', result
        print '############################################################'

    return


def Main():
    parser = argparse.ArgumentParser(prog=os.path.basename(__file__), description='Sample JET application')
    parser.add_argument("--user", nargs='?', help="Username for authentication by JET server (default:%(default)s)",
                        type=str, default=DEFAULT_JSD_USERNAME)
    parser.add_argument("--password", nargs='?', help="Password for authentication by JET server (default:%(default)s",
                        type=str, default=DEFAULT_JSD_PASSWORD)
    parser.add_argument("--address", nargs='?', help="Address of the JSD server. (default: %(default)s)",
                        type=str, default=DEFAULT_JSD_HOST)
    parser.add_argument("--port", nargs='?', help="Port number of the JSD request-response server. (default: %(default)s)",
                        type=int, default=DEFAULT_JSD_PORT)
    parser.add_argument("--certificate", nargs='?', help="Certificate full path. (default: %(default)s)",
                        type= str, default=DEFAULT_JSD_SSL_CERTIFICATE_PATH)
    args = parser.parse_args()

    # Create a client handler for connecting to server
    client = JetHandler()
    # Open session with Thrift Server
    try:
        client.OpenRequestResponseSession(device=args.address, port=args.port, user=args.user, password=args.password,
                                          ca_certs=args.certificate,client_id='T101')
        print 'Requesting for Interface services'
        FirewallTests(client)
        client.CloseRequestResponseSession()

    except Exception as tx:
        print '%s' % (tx.message)
        traceback.print_exc(file=sys.stdout)

    return

if __name__ == '__main__':
    Main()
