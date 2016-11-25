#!/usr/bin/python
__author__ = "Amish Anand"
__copyright__ = "Copyright (c) 2015 Juniper Networks, Inc."

"""
This script will be used by the yang file for retrieving the statistics
"""
import sys
import xmlrpclib
import httplib
from httplib import HTTPConnection
import socket
import xml.etree.ElementTree as ET
import os
import subprocess
from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlrpclib import Binary
import datetime
import time
from threading import Thread, Lock

server = SimpleXMLRPCServer(('127.0.0.1', 9191), logRequests=True, allow_none=True)
server.register_introspection_functions()
server.register_multicall_functions()
mutex = Lock()
SNABB_FILENAME = "/tmp/snabb_stats.xml"

class OpServer():
    """
    This RPC will return all the lwaftr counters for all or requested instance
    """
    def lwaftr(self):
	print "Called for lwaftr service"
        try:
            rpcclient = TimeoutServerProxy('http://128.0.0.100:9191', timeout=5)
            output = ''
            output = rpcclient.lwaftr()
        except Exception as e:
            output = "Failed to connect to jetapp " + e.message
        return output

    def top(self, instance_id):
	print "Called for top output"
	try:
	    rpcclient = TimeoutServerProxy('http://128.0.0.100:9191', timeout=5)
	    output = ''
	    output = rpcclient.top(instance_id)
	except Exception as e:
	    output = "Failed to connect to jetapp " + e.message
	return output

    def lwaftr_snmp(self):
	mutex.acquire()
	try:
	    with open(SNABB_FILENAME, "r") as f:
		output = f.read()
		mutex.release()
	except Exception as e:
	    print "lwaftr_snmp hit exception: ", e.message
	    output = self.lwaftr()
	    mutex.release()
	return output
	

def poll_snabb():
    """
    Poll for snabb counters every 5 seconds
    """
    while True:
        try:
            rpcclient = TimeoutServerProxy('http://128.0.0.100:9191', timeout=5)
            output = ''
            output = rpcclient.lwaftr()
        except Exception as e:
            output = "Failed to connect to jetapp " + e.message
	    exit(1)
	mutex.acquire()
	# Write the file now
	with open(SNABB_FILENAME, "w") as f:
	    f.write(output)
	mutex.release()
	time.sleep(5)


class MyHTTPConnect(httplib.HTTPConnection):
    def __init__(self, host, port=None, strict=None,
		timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.host = '128.0.0.100'
        self.port = 9191
        HTTPConnection.__init__(self,host, port, strict, timeout);

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
        self.sock.setsockopt(socket.IPPROTO_IP, 109,1)
        self.sock.connect((self.host, self.port))

class TimeoutHTTP(httplib.HTTP):
    _connection_class = MyHTTPConnect
    def __init__(self, host='', port=None, strict=None,
                timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        if port == 0:
            port = None
        self._setup(self._connection_class(host, port, strict, timeout))

    def getresponse(self, *args, **kw):
        return self._conn.getresponse(*args, **kw)

    def set_timeout(self, timeout):
        self._conn.timeout = timeout

class TimeoutTransport(xmlrpclib.Transport):
    def __init__(self, timeout=10, *args, **kwargs):
        xmlrpclib.Transport.__init__(self, *args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        conn = TimeoutHTTP(host)
        conn.set_timeout(self.timeout)
        return conn

class TimeoutServerProxy(xmlrpclib.ServerProxy):
    def __init__(self, uri, timeout=10, *l, **kw):
        kw['transport'] = TimeoutTransport(
            timeout=timeout, use_datetime=kw.get('use_datetime', 0))
        xmlrpclib.ServerProxy.__init__(self, uri, *l, **kw)


def main(argv):
    """
    Used to fetch the snabb instance information from the JET app.

    :param argv: Arguments for the command
    :return: Dictionary of instances state information
    """
    try:
        # log device initialized successfully
        print "Device initialized for the configuration updates"
        #Start a thread to do the polling
        t = Thread(target=poll_snabb)
        t.daemon = True
        t.start()
        opw = OpServer()
        server.register_instance(opw)
        print ("Starting the reactor")
        server.serve_forever()

    except Exception as e:
        # log device initialization failed
        print("JET app exiting due to exception: %s" %str(e.message))
        os._exit(0)
    return

if __name__ == '__main__':
    main(sys.argv)
