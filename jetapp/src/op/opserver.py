"""
Copyright (c) 2016, Juniper Networks, Inc.
All rights reserved.
"""

import os
from twisted.web import xmlrpc
import subprocess
from twisted.internet import reactor
from twisted.web import server

class OpServer(xmlrpc.XMLRPC):
    """
    This RPC will return all the lwaftr counters for all or requested instance
    """
    def xmlrpc_lwaftr(self):
        cmd = r"snabb snabbvmx query"
        output = subprocess.check_output(cmd, shell=True)
        if not output:
            print ('No Snabb instances are running')
            return None
        return output


def Main():
    try:
        # log device initialized successfully
        print "Device initialized for the configuration updates"
        opw = OpServer()
        reactor.listenTCP(9191, server.Site(opw))
        print ("Starting the reactor")
        reactor.run()

    except Exception as e:
        # log device initialization failed
        LOG.critical("JET app exiting due to exception: %s" %str(e.message))
        os._exit(0)
    return



if __name__ == '__main__':
    Main()
