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

import logging

DEFAULT_VALUE = "+"                           # Implies any value
DEFAULT_TOPIC = "#"                           # Implies all value
DEFAULT_IFD = r"+/+/+"                        # Regular expression for a default IFD
TOPIC_HEADER = r"/junos/events/kernel"        # Kernel event topic header
SYSLOG_TOPIC_HEADER = r"/junos/events/syslog" # Syslog event topic header
GENPUB_TOPIC_HEADER = r"/junos/events/genpub" # Generic pub event topic header
CONFIG_UPDATE = r"config-update"
OP_LIST = ["add", "delete", "change", "+"]    # List of the allowed operations
JET_NOTIFICATION_TOPIC_EVENT_TYPE_ROUTE = r"/junos/events/kernel/route/<op>/<args>"  
JET_NOTIFICATION_TOPIC_EVENT_TYPE_ROUTE_TABLE = r"/junos/events/kernel/route-table/<op>/<args>"  
JET_NOTIFICATION_TOPIC_EVENT_TYPE_INTERFACE_IFD = r"/junos/events/kernel/interfaces/ifd/<op>/<args>"  
JET_NOTIFICATION_TOPIC_EVENT_TYPE_INTERFACE_IFL = r"/junos/events/kernel/interfaces/ifl/<op>/<args>"  
JET_NOTIFICATION_TOPIC_EVENT_TYPE_INTERFACE_IFA = r"/junos/events/kernel/interfaces/ifa/<op>/<args>"  
JET_NOTIFICATION_TOPIC_EVENT_TYPE_INTERFACE_IFF = r"/junos/events/kernel/interfaces/iff/<op>/<args>"  
JET_NOTIFICATION_TOPIC_EVENT_TYPE_FIREWALL = r"/junos/events/kernel/firewall/filter/<op>/<args>"  
JET_NOTIFICATION_TOPIC_EVENT_TYPE_GENERIC = r"/junos/events/kernel/#"  

logger = logging.getLogger(__name__)

class CreateTopic(object):

    """
    Wrapper class for creating Notification Topic.

    """
    def CreateIFDTopic(self, op=DEFAULT_VALUE, ifd_name=DEFAULT_TOPIC):
        """
        This method creates the IFD topic.

        @param op: operation(ADD, DELETE, CHANGE, ALL), Default is ALL.
        @param ifd_name: ifd name to subscribe, Default is all ifds.

        @return: Returns the IFD topic object

        """
        data = {}
        if op not in OP_LIST:
            message = 'This operation %s provided is invalid' % op
            logger.error(message)
            raise Exception(message)
        data['op'] = op
        data['ifd_name'] = ifd_name
        data[
            'topic'] = "{0}/interfaces/ifd/{1}/{2}".format(TOPIC_HEADER, data['op'], data['ifd_name'])
        data['subscribed'] = 0
        self.topics_subscribed.append(data['topic'])
        logger.info('Successfully appended the topic %s' % data['topic'])
        return type('Topic', (), data)

    def CreateIFLTopic(
            self, op=DEFAULT_VALUE, ifd_name=DEFAULT_IFD, sub_unit=None):
        """
        This method creates IFL topic.

        @param op: operation(ADD, DELETE, CHANGE, ALL), Default is ALL.
        @param ifd_name: ifd name to subscribe, Default is all ifds.
        @param sub_unit: sub_unit is mandatory when interface name is passed.

        @return: Returns the IFL topic object

        """
        data = {}
        if op not in OP_LIST:
            message = 'This operation %s provided is invalid' % op
            logger.error(message)
            raise Exception(message)
        data['op'] = op
        if ((ifd_name != DEFAULT_IFD) and (sub_unit is None)):
            message = 'sub_unit is mandatory when interface name is passed'
            logger.error(message)
            raise Exception(message)

        elif ((ifd_name == DEFAULT_IFD) and (sub_unit is not None)):
            logger.info('sub_unit is valid only when interface name is passed')

        elif (ifd_name == DEFAULT_IFD):
            data['ifl_name'] = str(ifd_name)
        else:
            data['ifl_name'] = '%s.%s' % (ifd_name, sub_unit)
        data['subscribed'] = 0
        data['topic'] = "{0}/interfaces/ifl/{1}/{2}".format(TOPIC_HEADER, data['op'], data['ifl_name'])
        self.topics_subscribed.append(data['topic'])
        logger.info('Successfully appended the topic %s' % data['topic'])
        return type('Topic', (), data)

    def CreateIFFTopic(self, op=DEFAULT_VALUE, ifd_name=DEFAULT_IFD,
                       sub_unit=None, family_type=DEFAULT_VALUE):
        """
        This method creates IFF topic.

        @param op: operation(ADD, DELETE, CHANGE, ALL), Default is ALL.
        @param ifd_name: ifd name to subscribe, Default is all ifds.
        @param sub_unit: sub_unit is mandatory when interface name is passed.
        @param family_type: Default is all family_types.

        @return: Returns the IFF topic object

        """
        data = {}
        if op not in OP_LIST:
            message = 'This operation %s provided is invalid' % op
            logger.error(message)
            raise Exception(message)
        data['op'] = op
        if ((ifd_name != DEFAULT_IFD) and (sub_unit is None)):
            message = 'sub_unit is mandatory when interface name is passed'
            logger.error(message)
            raise Exception(message)
        elif ((ifd_name == DEFAULT_IFD) and (sub_unit is not None)):
            logger.info('sub_unit is valid only when interface name is passed')
        elif (ifd_name == DEFAULT_IFD):
            data['ifl_name'] = str(ifd_name)
        else:
            data['ifl_name'] = '%s.%s' % (ifd_name, sub_unit)

        data['family_type'] = family_type
        data['subscribed'] = 0
        data['topic'] = "{0}/interfaces/iff/{1}/{2}/{3}".format(
                                                                TOPIC_HEADER,
                                                                data['op'],
                                                                data['ifl_name'],
                                                                data['family_type'])
        self.topics_subscribed.append(data['topic'])
        logger.info('Successfully appended the topic %s' % data['topic'])
        return type('Topic', (), data)

    def CreateIFATopic(self, op=DEFAULT_VALUE, ifd_name=DEFAULT_IFD,
                       sub_unit=None, family_type=DEFAULT_VALUE, address=DEFAULT_TOPIC):
        """
        This method creates IFA topic.

        @param op: operation(ADD, DELETE, CHANGE, ALL), Default is ALL.
        @param ifd_name: ifd name to subscribe, Default is all ifds.
        @param sub_unit: sub_unit is mandatory when interface name is passed.
        @param family_type: Default is all family_types.
        @param address: Default is all address.

        @return: Returns the IFA topic object

        """
        data = {}
        if op not in OP_LIST:
            message = 'This operation %s provided is invalid' % op
            logger.error(message)
            raise Exception(message)
        data['op'] = op
        if ((ifd_name != DEFAULT_IFD) and (sub_unit is None)):
            message = "sub_unit is mandatory when interface name is passed"
            logger.error(message)
            raise Exception(message)
        elif ((ifd_name == DEFAULT_IFD) and (sub_unit is not None)):
            logger.info('sub_unit is valid only when interface name is passed')
        elif (ifd_name == DEFAULT_IFD):
            data['ifl_name'] = str(ifd_name)
        else:
            data['ifl_name'] = '%s.%s' % (ifd_name, sub_unit)
        data['family_type'] = family_type
        data['address'] = address
        data['subscribed'] = 0
        data['topic'] = "{0}/interfaces/ifa/{1}/{2}/{3}/{4}".format(
                                                                    TOPIC_HEADER,
                                                                    data['op'],
                                                                    data['ifl_name'],
                                                                    data['family_type'],
                                                                    data['address'])
        self.topics_subscribed.append(data['topic'])
        logger.info('Successfully appended the topic %s' % data['topic'])
        return type('Topic', (), data)


    def CreateFirewallTopic(self, op=DEFAULT_VALUE, filter_name=DEFAULT_TOPIC):
        """
        This method creates firewall topic.

        @param op: operation(ADD, DELETE, CHANGE, ALL), Default is ALL.
        @param filter_name: filter name to subscribe, Default is all filters.

        @return: Returns the firewall topic object

        """
        data = {}
        if op not in OP_LIST:
            message = 'This operation %s provided is invalid' % op
            logger.error(message)
            raise Exception(message)
        data['op'] = op
        data['filter_name'] = filter_name
        data['subscribed'] = 0
        data['topic'] = "{0}/firewall/filter/{1}/{2}".format(
                                                            TOPIC_HEADER,
                                                            data['op'],
                                                            data['filter_name'])
        self.topics_subscribed.append(data['topic'])
        logger.info('Successfully appended the topic %s' % data['topic'])
        return type('Topic', (), data)

    def CreateRouteTopic(
            self, op=DEFAULT_VALUE, family=DEFAULT_VALUE, address=DEFAULT_VALUE, prefix_length=DEFAULT_TOPIC):
        """
        This method creates route topic.

        @param op: operation(ADD, DELETE, CHANGE, ALL), Default is ALL.
        @param family: family to subscribe, Default is all family.
        @param address: address to subscribe, Default is all addresses.
        @param prefix_length: Default is all prefix lengths

        @return: Returns the route topic object

        """
        data = {}
        if op not in OP_LIST:
            message = 'This operation %s provided is invalid' % op
            logger.error(message)
            raise Exception(message)
        data['op'] = op
        data['family'] = family
        data['address'] = address
        data['prefix_length'] = prefix_length
        data['subscribed'] = 0
        data['topic'] = "{0}/route/{1}/{2}/{3}/{4}".format(TOPIC_HEADER,
                                                           data['op'],
                                                           data['family'],
                                                           data['address'],
                                                           data['prefix_length'])
        self.topics_subscribed.append(data['topic'])
        logger.info('Successfully appended the topic %s' % data['topic'])
        return type('Topic', (), data)

    def CreateRouteTableTopic(
            self, op=DEFAULT_VALUE, table_name=DEFAULT_VALUE, lr_name=DEFAULT_TOPIC):
        """
        This method creates route table topic.

        @param op: operation(ADD, DELETE, CHANGE, ALL), Default is ALL.
        @param table_name: table name to subscribe. Default is all tables
        @param lr_name: LR name to subscribe, Default is all

        @return: Returns the route table topic object

        """
        data = {}
        if op not in OP_LIST:
            message = 'This operation %s provided is invalid' % op
            logger.error(message)
            raise Exception(message)
        data['op'] = op
        data['table_name'] = table_name
        data['lr_name'] = lr_name
        data['subscribed'] = 0
        data['topic'] = "{0}/route-table/{1}/{2}/{3}".format(TOPIC_HEADER,
                                                             data['op'],
                                                             data['table_name'],
                                                             data['lr_name'])
        self.topics_subscribed.append(data['topic'])
        logger.info('Successfully appended the topic %s' % data['topic'])
        return type('Topic', (), data)

    def CreateGenericTopic(self):
        """
        This method creates a generic topic to subscribe all events.

        @return: Returns the generic topic object

        """
        data = {}
        data['subscribed'] = 0
        data['topic'] = '%s/%s' % (TOPIC_HEADER, DEFAULT_TOPIC)
        self.topics_subscribed.append(data['topic'])
        logger.info('Successfully appended the topic %s' % data['topic'])
        return type('Topic', (), data)

    def CreateStreamTopic (self, stream_topic):
        """
        This method creates a user-defined stream topic to subscribe for
        Thrift RPCs that have streaming responses.

        @return: Returns the stream topic object

        """

        if (' ' in stream_topic):
            logger.info('Invalid topic type, No space allowed in the topic')
            raise Exception('Invalid topic type, No space allowed in the topic')

        data = {}
        data['subscribed'] = 0
        data['topic'] = stream_topic
        self.topics_subscribed.append(data['topic']) 
        logger.info('Successfully appended the topic %s' % data['topic'])
        return type('Topic', (), data)

    def CreateSyslogTopic(self, event_id=DEFAULT_TOPIC):
        """
        This method creates the syslog topic.
        
        @param event_id: Syslog event id. Default is all syslog events.
        
        @return: Returns the Topic Object
        """
        
        data = {}
        data['event_id'] = event_id
        data[
            'topic'] = "{0}/{1}".format(SYSLOG_TOPIC_HEADER, data['event_id'])
        data['subscribed'] = 0
        self.topics_subscribed.append(data['topic'])
        logger.info('Successfully appended the topic %s' % data['topic'])
        return type('Topic', (), data)

    def CreateConfigUpdateTopic(self):
        """
        This method creates a topic to subscribe config-update events.

        @return: Returns the config-update topic object

        """
        data = {}
        data['subscribed'] = 0
        data['topic'] = '%s/%s' % (GENPUB_TOPIC_HEADER, CONFIG_UPDATE)
        self.topics_subscribed.append(data['topic'])
        logger.info('Successfully appended the topic %s' % data['topic'])
        return type('Topic', (), data)

