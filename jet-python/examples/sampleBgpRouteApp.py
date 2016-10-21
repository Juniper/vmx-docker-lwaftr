#!/usr/bin/env python
#
# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER
#
# Copyright (c) 2016 Juniper Networks, Inc.
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
Sample application file for the testing of BGP Route service hosted by the JSD server
Please modify the default parameters described below for proper testing.
Usage:
$python sampleBgpRoute.py

"""
import time
from jnpr.jet.JetHandler import *

# Device Details and Loging Credentials.
DEFAULT_JSD_HOST = 'localhost'
DEFAULT_JSD_PORT = 9090
DEFAULT_NOTIFICATION_PORT = 1883
DEFAULT_JSD_USERNAME = 'foo'
DEFAULT_JSD_PASSWORD = 'bar'

DEFAULT_CLIENT_ID = 'T_1234'
USER = 'foo'
PASSWORD = 'bar'
STREAM_TIMEOUT = 2

# For SSL based thrift server
DEFAULT_JSD_SSL_CERTIFICATE_PATH = None

# Logging Parameters
DEFAULT_LOG_FILE_NAME = os.path.basename(__file__).split('.')[0]+'.log'
DEFAULT_LOG_LEVEL = logging.DEBUG

# Following parameters are dummy. Please modify it before running this app.
D_PREFIX = '117.1.1.0'
D_PREFIX_LEN = '24'
D_ROUTE_TABLE = 'inet.0'
D_NEXT_HOP = '1.1.1.1'
D_PREFIX_UPD = '117.1.2.0'
P_COOKIE = '10'
L_PREF = '150'

def RouteInit(bgp):
    print '###################### INVOKING BgpRouteInitialize API #######################'
    strBgpReq = RoutingBgpRouteInitializeRequest()
    result = bgp.BgpRouteInitialize(strBgpReq)
    print 'Invoked BgpRouteInitialize API \nreturn = ', result.status
    #-Ve test repeated
    strBgpReq1 = RoutingBgpRouteInitializeRequest()
    result1 = bgp.BgpRouteInitialize(strBgpReq1)
    print 'Invoked BgpRouteInitialize API \nreturn = ', result1.status
    print '###################### INVOKING BgpRouteInitialize API #######################'

def RouteSet(bgp):
    print '###################### INVOKING BgpRouteSet API #######################'
    dp = RoutingRoutePrefix(RoutePrefixRoutePrefixAf(JnxBaseIpAddress(IpAddressAddrFormat(D_PREFIX))))
    rt = RoutingRouteTable(RtTableFormat=RouteTableRtTableFormat(rtt_name=RoutingRouteTableName(name=D_ROUTE_TABLE)))
    nh = JnxBaseIpAddress(IpAddressAddrFormat(D_NEXT_HOP))
    lp = RoutingBgpAttrib32(L_PREF)
    routeParams = RoutingBgpRouteEntry(dest_prefix= dp, dest_prefix_len= D_PREFIX_LEN, table= rt, protocol_nexthops= [nh],
                                   path_cookie= P_COOKIE, local_preference= lp, protocol= 2)
    updReq = RoutingBgpRouteUpdateRequest([routeParams])
    addRes = bgp.BgpRouteAdd(updReq)
    print 'Invoked Bgp Route Add API Status\nreturn = ', addRes.status
    print 'Bgp Route Add API Results\nreturn = ', addRes
    #-Ve test: Add same route again
    addRes = bgp.BgpRouteAdd(updReq)
    print 'Invoked Bgp Route Add API Status\nreturn = ', addRes.status
    print 'Bgp Route Add API Results\nreturn = ', addRes

    print '###################### INVOKING BgpRouteUpdate API #######################'
    #Test Update Route
    dp = RoutingRoutePrefix(RoutePrefixRoutePrefixAf(JnxBaseIpAddress(IpAddressAddrFormat(D_PREFIX_UPD))))
    rt = RoutingRouteTable(RtTableFormat=RouteTableRtTableFormat(rtt_name=RoutingRouteTableName(name=D_ROUTE_TABLE)))
    nh = JnxBaseIpAddress(IpAddressAddrFormat(D_NEXT_HOP))
    lp = RoutingBgpAttrib32(L_PREF)
    routeParams = RoutingBgpRouteEntry(dest_prefix= dp, dest_prefix_len= D_PREFIX_LEN, table= rt, protocol_nexthops= [nh],
                                   path_cookie= '90', local_preference= lp, protocol= 2)

    updReq = RoutingBgpRouteUpdateRequest([routeParams])
    addRes = bgp.BgpRouteUpdate(updReq)
    print 'Invoked Bgp Route Update API Status\nreturn = ', addRes.status
    print 'Bgp Route Update API Results\nreturn = ', addRes

    #-Ve test: Update same route again
    addRes = bgp.BgpRouteUpdate(updReq)
    print 'Invoked Bgp Route Update API Status\nreturn = ', addRes.status
    print 'Bgp Route Update API Results\nreturn = ', addRes

def RouteGet(bgp):
    print '###################### INVOKING BgpRouteGet API #######################'
    D_PREFIX = '117.0.0.0'; D_PREFIX_LEN ='8'
    dp = RoutingRoutePrefix(RoutePrefixRoutePrefixAf(JnxBaseIpAddress(IpAddressAddrFormat(D_PREFIX))))
    rt = RoutingRouteTable(RtTableFormat=RouteTableRtTableFormat(rtt_name=RoutingRouteTableName(name=D_ROUTE_TABLE)))

    routeParams = RoutingBgpRouteEntry(dest_prefix= dp, dest_prefix_len= D_PREFIX_LEN, table= rt, protocol= 2)
    bgpGetReq = RoutingBgpRouteGetRequest(bgp_route= routeParams, or_longer= True, route_count= "1", active_only= False)
    routeGetReply = bgp.BgpRouteGet(bgpGetReq,topic)
    print 'Invoked BgpRouteGet API\nreturn = ', routeGetReply
    time.sleep(STREAM_TIMEOUT)

def RouteDel(bgp):
    print '###################### INVOKING BgpRouteDelete API #######################'
    dp1 = RoutingRoutePrefix(RoutePrefixRoutePrefixAf(JnxBaseIpAddress(IpAddressAddrFormat(D_PREFIX))))
    dp2 = RoutingRoutePrefix(RoutePrefixRoutePrefixAf(JnxBaseIpAddress(IpAddressAddrFormat(D_PREFIX_UPD))))
    rt = RoutingRouteTable(RtTableFormat=RouteTableRtTableFormat(rtt_name=RoutingRouteTableName(name=D_ROUTE_TABLE)))

    routeParams = []
    routeParams.append(RoutingBgpRouteEntry(dest_prefix= dp1, dest_prefix_len= D_PREFIX_LEN, table= rt))
    routeParams.append(RoutingBgpRouteEntry(dest_prefix= dp2, dest_prefix_len= D_PREFIX_LEN, table= rt))

    bgpRemReq = RoutingBgpRouteRemoveRequest(0, routeParams)
    routeRemReply = bgp.BgpRouteRemove(bgpRemReq)
    print 'Invoked BgpRouteGet API\nreturn = ', routeRemReply
    time.sleep(STREAM_TIMEOUT)



# Callback handler function provided as an argument to the Subscribe api
eod = 0
def handleMessage (message):
    global eod
    global status
    if len(message) == 0:
        print "END OF DATA"
        eod = 1
    elif eod == 1:
        print message
        status = 1
        eod = 0
    else:
        str_res = RoutingBgpRouteGetReply()
        tbuf = TTransport.TMemoryBuffer(message)
        tmem_protocol = TBinaryProtocol.TBinaryProtocol(tbuf)

        str_res.read(tmem_protocol)
        print str_res.bgp_routes

def Main():
    # Create a client handler for connecting to server
    client = JetHandler()
    # Open session with Thrift Server
    try:
        client.OpenRequestResponseSession(device=DEFAULT_JSD_HOST, port=DEFAULT_JSD_PORT,
                                           user=USER, password=PASSWORD, ca_certs=None, client_id=DEFAULT_CLIENT_ID)
        evHandle = client.OpenNotificationSession(DEFAULT_JSD_HOST, DEFAULT_NOTIFICATION_PORT,
                                                  None, None, None, DEFAULT_MQTT_TIMEOUT, "", True)
        global topic
        topic = "SubscribedToBgpNotifications"
        stream = evHandle.CreateStreamTopic(topic)
        evHandle.Subscribe(stream, handleMessage, 2)
        print "Connected to Server and ",stream.topic
        bgp = client.GetRoutingBgpRoute()
        RouteInit(bgp)
        print "Verify on router using cli : show programmable-rpd clients"
        raw_input("<ENTER to Set route>")
        RouteSet(bgp)
        print "Verify on router using cli : show route protocol bgp-static"
        raw_input("<ENTER to Get route>")
        RouteGet(bgp)
        print "Compare API out put with CLI : show route protocol bgp-static"
        raw_input("<ENTER to Delete route>")
        RouteDel(bgp)
        print "Verify on router using cli : show route protocol bgp-static"
        raw_input("<Verify in router and ENTER>")
        print "Closing the Client"
        client.CloseNotificationSession()

    except Exception as tx:
        print '%s' % (tx.message)
    return

if __name__ == '__main__':
    Main()
