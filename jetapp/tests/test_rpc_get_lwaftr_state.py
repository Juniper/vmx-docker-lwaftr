#!/usr/bin/python
"""
This script will be used by the yang file for retrieving the statistics
"""
import sys
import xmlrpclib
import httplib
from httplib import HTTPConnection
import socket

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
        rpcclient = TimeoutServerProxy('http://128.0.0.100:9191', timeout=2)
        output = rpcclient.snabb_instances()

    except Exception as e:
        output = "No instances found, exception = " +  str(e.message)

    output = r"<output> " + str(output) + r"<\output>"
    print output

if __name__ == '__main__':
    main(sys.argv)