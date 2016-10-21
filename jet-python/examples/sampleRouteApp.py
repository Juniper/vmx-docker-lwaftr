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
Sample application file for the testing of Route service hosted by the JSD server
Please modify the default parameters described below for proper testing.
Usage:
$python sampleRouteApp.py --user <username> --password <password> --address <JSD host IP> --port <port number>

"""

import argparse
import os
import logging
import sys

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


# Route Testing parameters
DEFAULT_ROUTE_NEXTHOP_IP = '1.2.3.4'
DEFAULT_ROUTE_PREFERENCE_LIST = [5,15]
DEFAULT_ROUTE_METRIC_LIST = [3,5]
DEFAULT_ROUTE_APP_ID = '111:222'
DEFAULT_ROUTE_FAMILY_TYPE = FamilyType.af_unspec
DEFAULT_ROUTE_NEXTHOP_TYPE = None 
DEFAULT_ROUTE_PREFIX_AND_LENGTH = '1.1.1.1/32'
DEFAULT_ROUTE_GET_APP_ID = '0'
DEFAULT_ROUTE_GET_TABLE_NAME = '0'
DEFAULT_ROUTE_GET_PREFIX = ''

# Enable Logging to a file
logging.basicConfig(filename=DEFAULT_LOG_FILE_NAME, level=DEFAULT_LOG_LEVEL)
logging.StreamHandler(sys.stdout)

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
This API will perform all the route tests.
"""
def RouteTests(client):
    # All the route service APIs shall be tested here
    print 'RouteTests'
    # Create a client handlers for connecting to server
    route_handle = client.GetRouteService()
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

        result = route_handle.RouteGet(DEFAULT_ROUTE_GET_APP_ID,
                                       DEFAULT_ROUTE_GET_TABLE_NAME,
                                       DEFAULT_ROUTE_GET_PREFIX)
        print 'Invoked RouteGet, result= ', result.routes
        print 'Total length of list = ', len(result.routes)

        raw_input('Enter a key to continue?') 
        result = route_handle.RouteDelete(RouteConfig(
                                                      DEFAULT_ROUTE_APP_ID,
                                                      DEFAULT_ROUTE_FAMILY_TYPE,
                                                      DEFAULT_ROUTE_PREFIX_AND_LENGTH,
						      DEFAULT_ROUTE_NEXTHOP_TYPE,
                                                      None,
                                                      None, None,preference,metric,0, None)
                                          )
        print 'Invoked RouteDelete = ', result

        result = route_handle.RouteGet(DEFAULT_ROUTE_GET_APP_ID,
                                       DEFAULT_ROUTE_GET_TABLE_NAME,
                                       DEFAULT_ROUTE_GET_PREFIX)
        print 'Invoked RouteGet, result= ', result.routes
        print 'Total length of list = ', len(result.routes)

        raw_input('Enter a key to continue?') 
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
        client.OpenRequestResponseSession(device=args.address, port=args.port, user=args.user,
                                          password=args.password, ca_certs=args.certificate)
        print 'Requesting for Route Services'
        RouteTests(client)
        client.CloseRequestResponseSession()

    except Exception as tx:
        print '%s' % (tx.message)

    return

if __name__ == '__main__':
    Main()
