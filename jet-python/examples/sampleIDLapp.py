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
Sample application file for the testing of Route and management services hosted by the JSD server.
This application uses the raw Thrift APIs and not the client package.
Please modify the default parameters described below for proper testing. Please make sure that you generate the
python files from the idl and set the path properly in the imports of this sample file.
Usage:
$python sampleManagementApp.py --user <username> --password <password> --address <JSD host IP> --port <port number>

"""

import argparse
import os

from jnpr.jet.management import *
from jnpr.jet.management.ttypes import *
from jnpr.jet.management.constants import *
from jnpr.jet.route import *
from jnpr.jet.route.ttypes import *
from jnpr.jet.route.constants import *

from thrift.transport import TSocket
from thrift.transport import TSSLSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.protocol import TMultiplexedProtocol

# IMPORTANT: Following are the dummy parameters that will be used for testing
# different services. Please change the parameters for proper testing.

# Device Details and Loging Credentials.
DEFAULT_JSD_HOST = 'localhost'
DEFAULT_JSD_PORT = 9090
DEFAULT_JSD_USERNAME = 'foo'
DEFAULT_JSD_PASSWORD = 'bar'
DEFAULT_JSD_SSL_CERTIFICATE_PATH = None

# Route Testing parameters
DEFAULT_ROUTE_NEXTHOP_IP = '1.1.1.1'
DEFAULT_ROUTE_PREFERENCE_LIST = [5,15]
DEFAULT_ROUTE_METRIC_LIST = [3,5]
DEFAULT_ROUTE_APP_ID = '111:222'
DEFAULT_ROUTE_FAMILY_TYPE = FamilyType.af_unspec
DEFAULT_ROUTE_NEXTHOP_TYPE = None
DEFAULT_ROUTE_PREFIX_AND_LENGTH = '1.1.1.1/32'
DEFAULT_ROUTE_GET_APP_ID = '0'
DEFAULT_ROUTE_GET_TABLE_NAME = '0'
DEFAULT_ROUTE_GET_PREFIX = ''

# Management Testing parameters
DEFAULT_MANAGEMENT_CONFIG_FORMAT = ConfigFormatType.CONFIG_FORMAT_SET
DEFAULT_MANAGEMENT_CONFIG_DATABASE = ConfigDatabaseType.CONFIG_DB_SHARED
DEFAULT_MANAGEMENT_TEST_CONFIG = """
    set snmp view readall oid .1 include
    set snmp community test123 view readall
    set snmp community test123 authorization read-write
    """
DEFAULT_MANAGEMENT_TEST_RPC_NAME = 'get-interface-information'
DEFAULT_MANAGEMENT_TEST_RPC_ARGS = 'extensive:True, interface-name:em0'

class UniqueStore(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        if getattr(namespace, self.dest, self.default) is not None \
                and getattr(namespace, self.dest, self.default) is not self.default:
            parser.error(option_string + " appears several times.")
        setattr(namespace, self.dest, values)

def RouteTests(route_handle):
    # All the route service APIs shall be tested here
    print 'RouteTests'
    # Create a client handlers for connecting to server
    print '############################################################'

    for x in range(0, 1):
        nexthop_list = []
        n_list = NexthopInfo(nexthop_address=GatewayAddress(nexthop_ip=DEFAULT_ROUTE_NEXTHOP_IP))
        nexthop_list.append(n_list)
        preference = DEFAULT_ROUTE_PREFERENCE_LIST
        metric = DEFAULT_ROUTE_METRIC_LIST
        result = route_handle.RouteAdd(RouteConfig(
                                                   DEFAULT_ROUTE_APP_ID,
                                                   DEFAULT_ROUTE_FAMILY_TYPE,
                                                   DEFAULT_ROUTE_PREFIX_AND_LENGTH,
						   DEFAULT_ROUTE_NEXTHOP_TYPE,
                                                   nexthop_list,
                                                   None,None,preference,metric,0,None)
                                       )
                                                   
        print 'Invoked RouteAdd = ', result
        rflags = 1

        result = route_handle.RouteGet(DEFAULT_ROUTE_GET_APP_ID,
                                       DEFAULT_ROUTE_GET_TABLE_NAME,
                                       DEFAULT_ROUTE_GET_PREFIX)
        print 'Invoked RouteGet, result= ', result.routes
        print 'Total length of list = ', len(result.routes)
        
        result = route_handle.RouteDelete(RouteConfig(
                                                      DEFAULT_ROUTE_APP_ID,
                                                      DEFAULT_ROUTE_FAMILY_TYPE,
                                                      DEFAULT_ROUTE_PREFIX_AND_LENGTH,
						      DEFAULT_ROUTE_NEXTHOP_TYPE,
                                                      nexthop_list,
                                                      None,None,preference,metric,0,None)
                                          )
        print 'Invoked RouteDelete = ', result
        
        result = route_handle.RouteGet(DEFAULT_ROUTE_GET_APP_ID,
                                       DEFAULT_ROUTE_GET_TABLE_NAME,
                                       DEFAULT_ROUTE_GET_PREFIX)
        print 'Invoked RouteGet, result= ', result.routes
        print 'Total length of list = ', len(result.routes)

    return

def ManagementTests(mgmt_handle, user, password):
    # All the management service APIs shall be tested here
    # Create a client handler for connecting to server
    print ("Management Tests")
    print '############################################################'
    
    op_command = OperationCommand("show interfaces em0", OperationFormatType.OPERATION_FORMAT_CLI,
                                                        OperationFormatType.OPERATION_FORMAT_JSON);
    result = mgmt_handle.ExecuteOpCommand(op_command)
    print 'Invoked ExecuteOpCommand \nreturn = ', result

    snmp_config = """
            set snmp view readall oid .1 include
            set snmp community test123 view readall
            set snmp community test123 authorization read-write
        """
    commit = ConfigCommit(ConfigCommitType.CONFIG_COMMIT_SYNCHRONIZE, "Test comment", "")
    config = ConfigLoadCommit(snmp_config,ConfigFormatType.CONFIG_FORMAT_SET, ConfigDatabaseType.CONFIG_DB_SHARED,
                              ConfigLoadType.CONFIG_LOAD_REPLACE, commit)
    result = mgmt_handle.ExecuteCfgCommand(config)
    print 'Invoked ExecuteCfgCommand \nreturn = ', result

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


    try:
        # Make socket
        if (args.certificate is not None):
            # SSL connection
            if os.path.exists(args.certificate):
                transport = TSSLSocket.TSSLSocket(args.address,
                                                  args.port,
                                                  ca_certs=args.certificate)
            else:
                print('Certificate file %s does not exist' %(args.certificate))
                raise Exception('Given certificate %s does not exist'
                                %(args.certificate))
        else:
            transport = TSocket.TSocket(args.address, args.port)

        # Buffering is critical. Raw sockets are very slow
        transport = TTransport.TBufferedTransport(transport)
        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        mux_mgmt_protocol = TMultiplexedProtocol.TMultiplexedProtocol(protocol, "ManagementService")
        mux_route_protocol = TMultiplexedProtocol.TMultiplexedProtocol(protocol,"RouteService")
        transport.open()
        # IMPORTANT: The first service api to be called should be checkLogin
        mgmt_client = ManagementService.Client(mux_mgmt_protocol)
        result = mgmt_client.LoginCheck(args.user, args.password)
        if result is not True:
            raise ValueError('Login failed for User:%s' %args.user)
        print 'Invoked LoginCheck \nreturn = ', result
        print 'Requesting for mgmt tests'
        ManagementTests(mgmt_client, args.user, args.password)
        print 'Requesting for route tests'
        route_client = RouteService.Client(mux_route_protocol)
        RouteTests(route_client)
    except Exception as tx:
        print '%s' % (tx.message)
    return

if __name__ == '__main__':
    Main()

