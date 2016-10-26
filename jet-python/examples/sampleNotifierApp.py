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
# Usage: python sampleNotifierApp.py --address <address of JSD device> --port <port number> --bind_address <bind address>
#

import argparse
import os
import time
import logging
import sys

# JET shim layer imports
from jnpr.jet.JetHandler import *

# Default Notification topic parameters
DEFAULT_NOTIFICATION_IFD_NAME = "ge-1/0/4"
DEFAULT_NOTIFICATION_IFL_NAME = "ge-1/2/3"
DEFAULT_NOTIFICATION_IFL_UNIT = "35"

# Logging Parameters
DEFAULT_LOG_FILE_NAME = os.path.basename(__file__).split('.')[0]+'.log'
DEFAULT_LOG_LEVEL = logging.DEBUG

# Enable Logging to a file
logging.basicConfig(filename=DEFAULT_LOG_FILE_NAME, level=DEFAULT_LOG_LEVEL)

# To display the messages from junos-jet-api package on the screen uncomment the below line
myLogHandler = logging.getLogger()
myLogHandler.setLevel(logging.INFO)
logChoice = logging.StreamHandler(sys.stdout)
logChoice.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logChoice.setFormatter(formatter)
myLogHandler.addHandler(logChoice)

def handleEvents1(message):
    print "I am in first handle"
    print "Event Received : " + message['jet-event']['event-id']
    print "Attributes : ", message['jet-event']['attributes']
    return

def handleEvents2(message):
    print "I am in second handle"
    print "Event Received : " + message['jet-event']['event-id']
    print "Attributes : ", message['jet-event']['attributes']
    return


def Main():
    parser = argparse.ArgumentParser(prog=os.path.basename(__file__), description='Sample JET application')
    parser.add_argument("--address", nargs='?', help="Address of the JSD server. (default: %(default)s)",
                        type=str, default='localhost')
    parser.add_argument("--port", nargs='?', help="Port number of the JSD notification server. default: %(default)s",
                        type=int, default=1883)
    parser.add_argument("--bind_address", nargs='?', help="Client source address to bind.",
                        type=str, default="")
    args = parser.parse_args()

    try:

        # Create a client handler for connecting to server
        client = JetHandler()

        # open session with MQTT server
        evHandle = client.OpenNotificationSession(device=args.address, port=args.port, bind_address=args.bind_address)
        # different ways of creating topic
        ifdtopic = evHandle.CreateIFDTopic(op=evHandle.ALL, ifd_name=DEFAULT_NOTIFICATION_IFD_NAME)
        ifltopic = evHandle.CreateIFLTopic(evHandle.ALL,
                                           DEFAULT_NOTIFICATION_IFL_NAME,
                                           DEFAULT_NOTIFICATION_IFL_UNIT)
        ifatopic = evHandle.CreateIFATopic(evHandle.DELETE)
        ifftopic = evHandle.CreateIFFTopic(evHandle.CHANGE)
        rtmtopic = evHandle.CreateRouteTableTopic(evHandle.ALL)
        rttopic = evHandle.CreateRouteTopic(evHandle.ALL)
        fwtopic = evHandle.CreateFirewallTopic(evHandle.ALL)

        # Subscribe for events
        print "Subscribing to IFD notifications"
        evHandle.Subscribe(ifdtopic, handleEvents1)
        evHandle.Subscribe(ifltopic, handleEvents2)
        #evHandle.Subscribe(ifftopic, handleEvents1)
        evHandle.Subscribe(ifatopic, handleEvents1)
        evHandle.Subscribe(rtmtopic, handleEvents2)
        evHandle.Subscribe(rttopic, handleEvents2)
        evHandle.Subscribe(fwtopic, handleEvents1)
        ret = evHandle.Unsubscribe(ifftopic)
        if ret != 0:
            print ('Failed to unsubscribe %s' %ifftopic.topic)
        evHandle.Unsubscribe(ifdtopic)

        time.sleep(5)
        # Unsubscribe events
        print "Unsubscribe from all the event notifications"
        evHandle.Unsubscribe()

        # Close session
        print "Closing the Client"
        client.CloseNotificationSession()

    except Exception, tx:
        print '%s' % (tx.message)


    return

if __name__ == '__main__':
    Main()
