#!/usr/bin/python
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

""" Junos-Jet-API wrapper layer for developing JET notifications applications """

import paho.mqtt.client as mqtt
import json
import collections
import logging
from NotificationTopic import CreateTopic

decoder = json.JSONDecoder()
logger = logging.getLogger(__name__)


class NotifierMqtt(CreateTopic):

    """
    This class will create objects used to for notification service.

    """
    ADD = r"add"
    DELETE = r"delete"
    CHANGE = r"change"
    ALL = r"+"

    def __init__(self):
        self.mqtt_client = mqtt.Client()
        self.subscribed = 0
        self.handlers = None
        self.on_connectCBSet = False
        self.on_messageCBSet = False
        self.on_disconnectCBSet = False
        self.topics_subscribed = []

    def on_stream_message_cb (self, client, obj, msg):
        """
        This callback function will be used for Thrift streaming messages
        and won't be encoded in JSON Format but the thrift wire format.
        The read method corresponding to this data structure needs to be used
        to decode the data

        @param client: the client instance for this callback
        @param obj: the private user data as set in Client() or userdata_set()
        @param msg: an instance of Message. This is a class with members topic, payload, qos, retain

        """
        
        payload = msg.payload
        topic = msg.topic

        callback_called = False
        for cbs in self.handlers:
            if cbs != '#':
                if mqtt.topic_matches_sub(cbs, topic):
                    for cb in self.handlers.get(cbs, []):
                        cb(payload)
                        callback_called = True
        if callback_called == False:
            for cb in self.handlers.get('#', []):
                logger.debug('Sending data to callback %s' % cb)
                cb(payload)

    def on_message_cb(self, client, obj, msg):
        """
        This method will invoke the specified callback handler by the client app
        when a notification is received by the app based on the notification type.

        @param client: the client instance for this callback
        @param obj: the private user data as set in Client() or userdata_set()
        @param msg: an instance of Message. This is a class with members topic, payload, qos, retain

        """
        payload = msg.payload
        topic = msg.topic
        json_data = None
        json_data, end = decoder.raw_decode(payload)
        if json_data is None:
            logger.error('Received event has invalid JSON format')
            logger.error('Received payload: %s' % payload)
        if len(payload) != end:
            logger.error('Received event has additional invalid JSON format')
            logger.error('It has the following additional content: %s' % payload[end:])
        callback_called = False
        for cbs in self.handlers:
            if cbs != '#':
                if mqtt.topic_matches_sub(cbs, topic):
                    for cb in self.handlers.get(cbs, []):
                        cb(json_data)
                        callback_called = True

        if callback_called == False:
            for cb in self.handlers.get('#', []):
                logger.debug('Sending data to callback %s' % cb)
                cb(json_data)

    def Subscribe(self, subscriptionType, handler=None, qos=0):
        """
        This method subscribes to a specific topic the client app is interested
        in. This takes subscription type and the callback function as parameters.
        When the notification for the subscribed topic is received, user passed
        callback function will be called. Callback function receives the
        notification message in json format.

        @param subscriptionType : Type of notification user wants to subscribe to
        @param handler: Callback function for each notification

        """
        topic = subscriptionType.topic
        self.mqtt_client.subscribe(topic, qos)
        subscriptionType.subscribed = 1
        
        if(handler):
            self.handlers[topic].add(handler)
        logger.info('Successfully subscribed to event:%s' %subscriptionType.topic)

    def Unsubscribe(self, subscriptionType=None):
        """
        This method takes the topic as argument and unsubscribes to the given topic.
        If topic name is not given as argument (no arguments), this method
        unsubscribes to all the topics which app already subscribed for.

        @param subscriptionType: Notification type that user wants to unsubscribe from.
        @return 0 on successful unsubscription and -1 on failure

        """
        if subscriptionType is None:
            self.mqtt_client.unsubscribe(self.topics_subscribed)
            self.handlers = collections.defaultdict(set)
            logger.info('Successfully unsubscribed from all notifications')
            return 0
        elif not isinstance(subscriptionType, type):
            message = 'Invalid subscription topic: ' + subscriptionType
            logger.error(message)
            raise Exception(message)
    
        else:
            for item in self.topics_subscribed:
                if (item == subscriptionType.topic and subscriptionType.subscribed == 1):
                    self.mqtt_client.unsubscribe(subscriptionType.topic)
                    self.mqtt_client.unsubscribe(subscriptionType.topic)
                    self.handlers.pop(str(subscriptionType.topic), None)
                    logger.info('Successfully unsubscribed %s' % subscriptionType.topic)
                    return 0
    
            # Failed case
            logger.info('You have not subscribed to %s. Failed to unsubscribe' % subscriptionType.topic)
            return -1

    def SetCallbackOnConnect(self, cb):
        """
        This method sets the callback on connect.

        @param cb: callback to set.

        """
        if (self.subscribed == 0):
            self.mqtt_client.on_connect = cb
            self.on_connectCBSet = True

    def UnsetCallbackOnConnect(self):
        """
        This method unset the callback on connect.

        """
        self.mqtt_client.on_connect = None
        self.on_connectCBSet = False

    def SetCallbackOnDisconnect(self, cb):
        """
        This method sets the callback on disconnect.

        @param cb: callback to set

        """
        self.mqtt_client.on_disconnect = cb
        self.on_disconnectCBSet = True

    def UnsetCallbackOnDisconnect(self):
        """
        This method unsets the callback on disconnect.

        """
        self.mqtt_client.on_disconnect = None
        self.on_disconnectCBSet = False

    def SetCallbackOnMessage(self, cb, subscriptionType="#"):
        """
        This method sets the callback on message.

        @param cb: callback to set
        @param subscriptionType: the message topic to set callback

        """
        if cb:
            self.handlers[subscriptionType].add(cb)
            self.on_messageCBSet = True

    def UnsetCallbackOnMessage(self, subscriptionType="#"):
        """
        This method unset the callback for the given subscription type.

        @param subscriptionType: message topic

        """
        self.handlers.pop(str(subscriptionType), None)
        self.on_messageCBSet = False

    def GetCallbacks(self):
        """
        This method retrieves all the callbacks.

        """
        return self.handlers

    def Close(self):
        """
        This method closes the mqtt connection.

        """
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        del self
