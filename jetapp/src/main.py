#!/usr/bin/env python
__author__ = "Amish Anand"
__copyright__ = "Copyright (c) 2015 Juniper Networks, Inc."

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
# Please make sure to run this file as a root user


import argparse
import os
from device import Device
from threading import Thread
from conf.confParser import ParseNotification
from op.opserver import OpServer
from twisted.internet import reactor
from twisted.web import server
from utils.jetapplog import LOG


def Main():
    parser = argparse.ArgumentParser(prog=os.path.basename(__file__), description='Snabb VMX integration JET app')
    parser.add_argument("--host", required=True, help="Host address of the JSD server",
                        type=str)
    parser.add_argument("--notification_port", nargs='?', help="Port number of the JSD notification server. default: %(default)s",
                        type=int, default=1883)
    parser.add_argument("--user", required=True, help="Username for authentication by JET server (default:%(default)s)",
                        type=str)
    parser.add_argument("--password", required=True, help="Password for authentication by JET server (default:%(default)s",
                        type=str)
    args = parser.parse_args()
    device = Device(args.host, args.user, args.password, args.notification_port)

    dispatchFunction = ParseNotification(device)
    dispatchThread = Thread(target=dispatchFunction)
    dispatchThread.setDaemon(True)
    dispatchThread.start()
    try:
        device.initialize()
        # log device initialized successfully
        print "Device initialized for the configuration updates"
        opw = OpServer()
        reactor.listenTCP(9191, server.Site(opw))
        LOG.info("Starting the reactor")
        reactor.run()

    except Exception as e:
        # log device initialization failed
        LOG.critical("JET app exiting due to exception: %s" %str(e.message))
        os._exit(0)
    return

if __name__ == '__main__':
    Main()