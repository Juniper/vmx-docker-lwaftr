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
Sample application file for the testing of Management service hosted by the JSD server
Please modify the default parameters described below for proper testing.
Usage:
$python sampleManagementApp.py --user <username> --password <password> --address <JSD host IP> --port <port number>

"""

import argparse
import os
import logging

# JET shim layer imports
from jnpr.jet.JetHandler import *
from jnpr.jet.management import ManagementService
from jnpr.jet.management.ttypes import *

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

# Enable Logging to a file
logging.basicConfig(filename=DEFAULT_LOG_FILE_NAME, level=DEFAULT_LOG_LEVEL)

# To display the messages from junos-jet-api package on the screen uncomment the below lines
"""
myLogHandler = logging.getLogger()
myLogHandler.setLevel(logging.INFO)
logChoice = logging.StreamHandler(sys.stdout)
logChoice.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logChoice.setFormatter(formatter)
myLogHandler.addHandler(logChoice)
"""

"""
This API will perform all the management tests.
"""
def ManagementTests(client, user, password):
    # All the management service APIs shall be tested here
    # Create a client handler for connecting to server
    mgmt_handle = client.GetManagementService()

    snmp_config = """
            set snmp view readall oid .1 include
            set snmp community test123 view readall
            set snmp community test123 authorization read-write
        """
    commit = ConfigCommit(ConfigCommitType.CONFIG_COMMIT, "Test comment", "")
    config = ConfigLoadCommit(snmp_config,ConfigFormatType.CONFIG_FORMAT_SET, ConfigDatabaseType.CONFIG_DB_SHARED,
                              ConfigLoadType.CONFIG_LOAD_REPLACE, commit)
    result = mgmt_handle.ExecuteCfgCommand(config)
    print 'Invoked ExecuteCfgCommand \nreturn = ', result

    snmp_config = """
        snmp {
            view readall {
                oid .1 include;
            }

            community test123 {
                view readall;
                authorization read-write;
            }
        }
        """
    config = ConfigLoadCommit(snmp_config,ConfigFormatType.CONFIG_FORMAT_TEXT, ConfigDatabaseType.CONFIG_DB_SHARED,
                              ConfigLoadType.CONFIG_LOAD_MERGE, commit)
    result = mgmt_handle.ExecuteCfgCommand(config)
    print 'Invoked ExecuteCfgCommand \nreturn = ', result

    snmp_config = """
            <snmp>
                <view>
                    <name>readall</name>
                    <oid>
                        <name>.1</name>
                        <include/>
                    </oid>
                    <oid>
                        <name>.1.3</name>
                        <exclude/>
                    </oid>
                </view>
                <community>
                    <name>test123</name>
                    <view>readall</view>
                    <authorization>read-write</authorization>
                </community>
                <community>
                    <name>test1234</name>
                    <view>readall</view>
                    <authorization>read-write</authorization>
                </community>
            </snmp>
        """
    config = ConfigLoadCommit(snmp_config,ConfigFormatType.CONFIG_FORMAT_XML, ConfigDatabaseType.CONFIG_DB_SHARED,
                              ConfigLoadType.CONFIG_LOAD_REPLACE, commit)
    result = mgmt_handle.ExecuteCfgCommand(config)
    print 'Invoked ExecuteCfgCommand \nreturn = ', result

    ############ Example for operational command execution ############
    op_command = OperationCommand("show interfaces em0", OperationFormatType.OPERATION_FORMAT_CLI,
                                                        OperationFormatType.OPERATION_FORMAT_CLI);
    result = mgmt_handle.ExecuteOpCommand(op_command)
    print 'Invoked OperationCommand \nreturn = ', result

    json_query = "{ \"get-interface-information\" : { \"interface-name\" : \"em0\" } }"
    op_command = OperationCommand(json_query,
                                                        OperationFormatType.OPERATION_FORMAT_JSON,
                                                        OperationFormatType.OPERATION_FORMAT_JSON);
    result = mgmt_handle.ExecuteOpCommand(op_command)
    print 'Invoked OperationCommand \nreturn = ', result

    xml_query = "<get-interface-information > <interface-name>em0</interface-name> <detail/> </get-interface-information>"
    op_command = OperationCommand(xml_query, in_format=OperationFormatType.OPERATION_FORMAT_XML,
                                                        out_format=OperationFormatType.OPERATION_FORMAT_XML);
    result = mgmt_handle.ExecuteOpCommand(op_command)
    print 'Invoked OperationCommand \nreturn = ', result

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
                                          ca_certs=args.certificate)
        print 'Requesting for Management services'
        ManagementTests(client, args.user, args.password)
        client.CloseRequestResponseSession()

    except Exception as tx:
        print '%s' % (tx.message)

    return

if __name__ == '__main__':
    Main()