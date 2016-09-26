#!/usr/bin/python
"""
This script will be used by the yang file for retrieving the statistics
"""
import sys
import xmlrpclib
import httplib
from httplib import HTTPConnection
import socket
import xml.etree.ElementTree as ET

class MyHTTPConnect(httplib.HTTPConnection):
    def __init__(self, host, port=None, strict=None,
		        timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.host = host #'128.0.0.100'
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


def PRINT_TAG(node, tag):
    if node.tag == tag:
        print '<'+tag+'>'
	if node.text.strip() == "":
	    print "n/a"
	else:
            print node.text.strip()
        print '</'+tag+'>'
    return

def snabb_statistics(query_output):
    root = ET.fromstring(query_output)
    for instance in root:
        print ("<statistics>")
        for child_instance in instance:
            PRINT_TAG(child_instance,"id")
            if child_instance.tag == "apps":
                for app_child in child_instance:
                    if app_child.tag == "lwaftr":
                        for lwaftr_child in app_child:
                            # Parse all the attributes and print it
                            PRINT_TAG(lwaftr_child,'drop-all-ipv4-iface-bytes')
                            PRINT_TAG(lwaftr_child,'drop-all-ipv4-iface-packets')
                            PRINT_TAG(lwaftr_child,'drop-all-ipv6-iface-bytes')
                            PRINT_TAG(lwaftr_child,'drop-all-ipv6-iface-packets')
                            PRINT_TAG(lwaftr_child,'drop-bad-checksum-icmpv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-bad-checksum-icmpv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-in-by-policy-icmpv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-in-by-policy-icmpv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-in-by-policy-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-in-by-policy-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-in-by-rfc7596-icmpv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-in-by-rfc7596-icmpv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-ipv4-frag-invalid-reassembly')
                            PRINT_TAG(lwaftr_child,'drop-ipv4-frag-random-evicted')
                            PRINT_TAG(lwaftr_child,'drop-ipv6-frag-invalid-reassembly')
                            PRINT_TAG(lwaftr_child,'drop-ipv6-frag-random-evicted')
                            PRINT_TAG(lwaftr_child,'drop-misplaced-not-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-misplaced-not-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-misplaced-not-ipv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-misplaced-not-ipv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-no-dest-softwire-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-no-dest-softwire-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-no-source-softwire-ipv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-no-source-softwire-ipv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-out-by-policy-icmpv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-out-by-policy-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-over-mtu-but-dont-fragment-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-over-mtu-but-dont-fragment-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-over-rate-limit-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-over-rate-limit-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-over-time-but-not-hop-limit-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-over-time-but-not-hop-limit-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-too-big-type-but-not-code-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-too-big-type-but-not-code-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-ttl-zero-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'drop-ttl-zero-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'drop-unknown-protocol-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-unknown-protocol-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'drop-unknown-protocol-ipv6-bytes')
                            PRINT_TAG(lwaftr_child,'drop-unknown-protocol-ipv6-packets')
                            PRINT_TAG(lwaftr_child,'hairpin-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'hairpin-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'in-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'in-ipv4-frag-needs-reassembly')
                            PRINT_TAG(lwaftr_child,'in-ipv4-frag-reassembled')
                            PRINT_TAG(lwaftr_child,'in-ipv4-frag-reassembly-unneeded')
                            PRINT_TAG(lwaftr_child,'in-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'in-ipv6-bytes')
                            PRINT_TAG(lwaftr_child,'in-ipv6-frag-needs-reassembly')
                            PRINT_TAG(lwaftr_child,'in-ipv6-frag-reassembled')
                            PRINT_TAG(lwaftr_child,'in-ipv6-frag-reassembly-unneeded')
                            PRINT_TAG(lwaftr_child,'in-ipv6-packets')
                            PRINT_TAG(lwaftr_child,'ingress-packet-drops')
                            PRINT_TAG(lwaftr_child,'memuse-ipv4-frag-reassembly-buffer')
                            PRINT_TAG(lwaftr_child,'memuse-ipv6-frag-reassembly-buffer')
                            PRINT_TAG(lwaftr_child,'out-icmpv4-bytes')
                            PRINT_TAG(lwaftr_child,'out-icmpv4-packets')
                            PRINT_TAG(lwaftr_child,'out-icmpv6-bytes')
                            PRINT_TAG(lwaftr_child,'out-icmpv6-packets')
                            PRINT_TAG(lwaftr_child,'out-ipv4-bytes')
                            PRINT_TAG(lwaftr_child,'out-ipv4-frag')
                            PRINT_TAG(lwaftr_child,'out-ipv4-frag-not')
                            PRINT_TAG(lwaftr_child,'out-ipv4-packets')
                            PRINT_TAG(lwaftr_child,'out-ipv6-bytes')
                            PRINT_TAG(lwaftr_child,'out-ipv6-frag')
                            PRINT_TAG(lwaftr_child,'out-ipv6-frag-not')
                            PRINT_TAG(lwaftr_child,'out-ipv6-packets')
        print ("</statistics>")


def main(argv):
    """
    Parse the arguments to determine if the call is for showing the
    statistics of all or one instance.
    :param argv: Arguments for the command
    :return: Dictionary of instances or statistics
    """
    try:
        rpcclient = TimeoutServerProxy('http://128.0.0.100:9191', timeout=5)
        output = ''
        output = rpcclient.lwaftr()
    except Exception as e:
        output = "Failed to connect to jetapp " + e.message
        return
    if (output != None):
        snabb_statistics(output)
        print output
    else:
        print "No instances found"
if __name__ == '__main__':
    main(sys.argv)