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
Junos-Jet-API wrapper layer for developing JET applications
"""

import struct
import traceback
import logging
from importlib import import_module

from thrift import Thrift
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport import TSSLSocket
from thrift.protocol import TBinaryProtocol
from thrift.protocol.TMultiplexedProtocol import TMultiplexedProtocol

from jnpr.jet.firewall import *
from jnpr.jet.route import *
from jnpr.jet.management import *
from jnpr.jet.interfaces import *
from jnpr.jet.authentication import *
from jnpr.jet.routing_prpd_common import *
from jnpr.jet.jnxBase_jnx_addr import *
from jnpr.jet.routing_bgproute import *
from jnpr.jet.routing_prpd import *

from jnpr.jet import *

# Route Service imports
from jnpr.jet.route.constants import *
from jnpr.jet.route.ttypes import *
 
# Management Service imports
from jnpr.jet.management.ttypes import *
from jnpr.jet.management.constants import *
 
# Interface Service imports
from jnpr.jet.interfaces.ttypes import *
from jnpr.jet.interfaces.constants import *
 
# Firewall Service imports
from jnpr.jet.firewall.ttypes import *
from jnpr.jet.firewall.constants import *

# Bgp Route service imports
from jnpr.jet.routing_bgproute.ttypes import *
from jnpr.jet.routing_bgproute.constants import *

# PRPD common imports
from jnpr.jet.routing_prpd_common.ttypes import *
from jnpr.jet.routing_prpd_common.constants import *

# JNX address imports
from jnpr.jet.jnxBase_jnx_addr.ttypes import *
from jnpr.jet.jnxBase_jnx_addr.constants import *

# PRPD Service imports
from jnpr.jet.routing_prpd.ttypes import *
from jnpr.jet.routing_prpd.constants import *

# JSD Management service imports
from jnpr.jet.authentication.ttypes import *
from jnpr.jet.authentication.constants import *


from importlib import import_module


from notification.NotificationHandler import *

DEVICE_DEFAULT_PORT = 9090          # Default port for client to connect to the device
DEVICE_DEFAULT_IP = '127.0.0.1'     # Default JET request response server host address
DEVICE_DEFAULT_TRANSPORT = None     # Default Transport mode, without any security binding
DEVICE_TLS_TRANSPORT = 'tls'        # TLS Security binding not supported yet.
DEFAULT_MQTT_PORT = 1883            # Default JET notification port
DEFAULT_MQTT_IP = '127.0.0.1'       # Default JET address for MQTT
DEFAULT_MQTT_TIMEOUT = 60           # Default Notification channel timeout

logger = logging.getLogger(__name__)

class JetHandler():
    """
    This class provides easy methods to connect to the JET Request Response and Notification servers
    and to access all the JET services.

    """
    def __init__(self):
        pass

    def OpenRequestResponseSession(self, transport_type=DEVICE_DEFAULT_TRANSPORT,
                                   device=DEVICE_DEFAULT_IP, port=DEVICE_DEFAULT_PORT,
                                   timeout=None, ca_certs=None, user=None,
                                   password=None, client_id = "empty",
				   **trnsprt_args):
        """
        Create a request response session with the JET server. Raises exception due to Thrift exceptions or
        SSL certificate is missing or user credentials are not valid.

        @param transport_type: Thrift transport channel. Default is TLS
        @param device: JET server IP address. Default is localhost
        @param port: JET server port number. Default is 9090
        @param timeout: Timeout parameter in seconds. Default is None so the calls will be blocked
        @param ca_certs: Certificate path needed for the SSL based transport
        @param user: Username on the JET server, used for authentication and authorization.
	@param client_id: Client ID provided by the JET app
        @param password: Password to access the JET server, used for authentication and authorization.

        @return JET request response object

        """

        self.transport_type = transport_type
        self.device = device
        self.port = port
        self.ca_certs = ca_certs
        try:
            # Make socket
            logger.info('Initiating connection to the JET request response server(%s:%d)' % (device, port))
            if ca_certs:
                self.ca_certs = os.path.abspath(ca_certs)
                if os.path.exists(self.ca_certs):
                    self.transport = TSSLSocket.TSSLSocket(self.device,
                                                           self.port,
                                                           ca_certs=self.ca_certs)
                    logger.info('Created the SSL transport socket %r'
                                  %(self.transport))
                else:
                    logger.error('Certificate file %s does not exist' %(ca_certs))
                    raise Exception('Given certificate %s does not exist'
                                    %(ca_certs))
            else:
                self.transport = TSocket.TSocket(self.device, self.port)

            # Convert the timeout to milliseconds before setting it for Thrift transport
            if (timeout != None):
                self.transport.setTimeout(timeout*1000)
                logger.info('setting timeout to %d seconds' %(timeout))

            # Buffering is critical. Raw sockets are very slow
            self.transport = TTransport.TBufferedTransport(self.transport)

            # Wrap in a protocol
            protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

            # for holding client stub references
            self.clients = {}

            # for holding service name and service classes
            self.services = {}

            jet_directory = os.path.dirname(os.path.realpath(__file__))
            jet_module = "jnpr.jet."
            listing = os.listdir(jet_directory)
            for svc_dir in listing:
                if (svc_dir == 'notification' or svc_dir == 'shared' or svc_dir == 'routing_prpd_common'
                    or svc_dir == 'jnxBase_jnx_addr' or svc_dir == 'server-extension'):
                  continue
                pathname = os.path.join(jet_directory, svc_dir)
                if os.path.isdir(pathname):
                    const_mod = import_module(jet_module + svc_dir + '.' + 'constants')
                    svc_name = getattr(const_mod, "SERVICE_NAME")
                    svc_mod = import_module(jet_module + svc_dir)
                    service_class = svc_name
                    # just to keep legacy name of class, can rename the class to service name in future        
                    if (service_class == 'InterfaceService'):
                        service_class = 'InterfacesService'
                    self.clients[svc_name] = getattr(svc_mod, service_class)

            for service in self.clients:
                mux_protocol = TMultiplexedProtocol(protocol,service)
                self.services[service] = self.clients[service].Client(mux_protocol)
                setattr(self, 'Get' + service, self.make_service_method(service))

            self.authentication = self.services[authentication.constants.SERVICE_NAME]

            # Connect to JET server
            self.transport.open()
            logger.debug('Connected to the JET server')

            if (user is not None and len(user) > 0):
                login_request = AuthenticationLoginRequest();
                login_request.user_name = user
                login_request.password = password
                login_request.client_id = client_id 
                login_reply = self.authentication.LoginCheck(login_request)

                if login_reply.result == 1:
                    logger.info('login check successful')
                else:
                    logger.error('User %s specified is not permitted' %(user))
                    raise Exception('User %s specified is not permitted'%user)

        except Thrift.TException, tx:
            logger.error('%s' %(tx.message))
            raise Exception(tx.message)


    def OpenNotificationSession(self, device=DEFAULT_MQTT_IP, port=DEFAULT_MQTT_PORT,
                                user=None, password=None, tls=None, keepalive=DEFAULT_MQTT_TIMEOUT,
                                bind_address="", is_stream = False):
        """
        Create a request response session with the  JET server. Raises exception in case
        of invalid arguments or when JET notification server is not accessible.

        @param device: JET Server IP address. Default is localhost
        @param port: JET Notification port number. Default is 1883
        @param user: Username on the JET server, used for authentication and authorization.
        @param password: Password to access the JET server, used for authentication and authorization.
        @param keepalive: Maximum period in seconds between communications with the broker. Default is 60.
        @param bind_address: Client source address to bind. Can be used to control access at broker side.

        @return: JET Notification object.

        """

        try:
            self.notifier = NotifierMqtt()
            logger.info('Connecting to JET notification server')
            self.notifier.mqtt_client.connect(device, port, keepalive, bind_address)
            self.notifier.mqtt_client.loop_start()
            self.notifier.handlers = collections.defaultdict(set)
            if is_stream == True:
                self.notifier.mqtt_client.on_message = self.notifier.on_stream_message_cb
            else:
                self.notifier.mqtt_client.on_message = self.notifier.on_message_cb

        except struct.error as err:
            message = err.message
            err.message = 'Invalid argument value passed in %s at line no. %s\nError: %s' \
                          % (traceback.extract_stack()[0][0], traceback.extract_stack()[0][1],  message)
            logger.error('%s' %(err.message))
            raise err
        except Exception, tx:
            tx.message = 'Could not connect to the JET notification server'
            logger.error('%s' %(tx.message))
            raise Exception(tx.message)

        return self.notifier

    def CloseNotificationSession(self):
        """
        This method closes the JET Notification channel.

        """

        self.notifier.Close()
        logger.info('JET notification channel closed by user.')


    def GetNotificationService(self):
        """
        This method will return object that will provide access to notification
        service methods.

        """
        return self.notifier

    def CloseRequestResponseSession(self):
        """
        This method will close the communication channel between client and JET server.

        """
        self.transport.close()

    def GetService(self, service_name):
         """
         Generic method to get handle for any service by name.
         """
         return self.services[service_name]

    def make_service_method(self, service_name):
        def _function():
            return self.services[service_name]
        return _function

    def GetService(self, service_name):
         """
         Generic method to get handle for any service by name.
         """
         return self.services[service_name]

    def make_service_method(self, service_name):
        def _function():
            return self.services[service_name]
        return _function
