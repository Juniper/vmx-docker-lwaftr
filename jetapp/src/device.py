#!/usr/bin/env python
__author__ = "Amish Anand"
__copyright__ = "Copyright (c) 2015 Juniper Networks, Inc."

import sys
from jnpr.jet.JetHandler import *
from utils.sanity import Sanity
from conf.callback import SnabbCallback
from utils.jetapplog import LOG
import time

class Device(object):

    """
    Main class to establish the connection and starting the twisted server
    """

    @property
    def user(self):
        """
        :return: the login user accessing the JET services
        """
        return self._auth_user

    @property
    def password(self):
        """
        :return: the password of user accessing the JET services
        """
        return self._auth_pwd

    @property
    def logfile(self):
        """
        :return: existing logfile object
        """
        return self._logfile

    @logfile.setter
    def logfile(self, value):
        # got an existing file that we need to close
        if (not value) and (None != self._logfile):
            rc = self._logfile.close()
            self._logfile = False
            return rc

        if sys.version < '3':
            if not isinstance(value, file):
                raise ValueError("value must be a file object")
        else:
            import io
            if not isinstance(value, io.TextIOWrapper):
                raise ValueError("value must be a file object")

        self._logfile = value
        return self._logfile

    @property
    def host(self):
        return self._host

    @property
    def mqttPort(self):
        return self._mqtt_port


    def __init__(self, host, user, pwd, port = 1883, **kvargs):
        """
        Device object constructor
        :param str host: Hostname of the VMX
        :param int port: Notification port, default = 1883
        :param str user: Username
        :param str pwd: Password
        """

        self._host = host
        self._mqtt_port = port
        self._auth_user = user
        self._auth_pwd = pwd
        self.jetClient = JetHandler()
        # Initialize the instance variables
        self.connected = False
        self.opServer = None
        self.evHandle = None

    def initialize(self, *vargs, **kvargs):
        """
        Open the Request Response Connection
        open the notification connection
        start the worker threads
        start the twisted server
        :param vargs:
        :param kvargs:
        :return:
        """
        # Create a request response session
        try:
            sanityObj = Sanity(self)
            sanityResult = sanityObj.YangModulePresent()
            if (False == sanityResult):
                # log the message
                LOG.critical("Yang module not present")
                os._exit(0)
            LOG.info("YANG module present")

            sanityResult = sanityObj.NotificationConfigPresent()
            if (False == sanityResult):
                # Apply the commit notification config of the vmx
                print("Commit notification config is not present")
                result = sanityObj.CommitNotificationConfig()
                if (False == result):
                    # Failed to apply the notification config on the vmx
                    LOG.critical("Failed to apply commit notification config on the VMX")
                    # log the message
                    os._exit(0)
                else:
                    LOG.info("Applied the commit notification config successfully")
            else:
                # log that Notification config is present
                LOG.info("Commit Notification config already present")
                pass

            # Open notification session
            self.messageCallback = SnabbCallback(self)
            self.evHandle = self.jetClient.OpenNotificationSession(
                device=self._host, port=self._mqtt_port)
            cutopic = self.evHandle.CreateConfigUpdateTopic()
            self.evHandle.Subscribe(cutopic, self.messageCallback)
            # subscription completed
            LOG.info("Notification channel opened now")
            self.connected = True
            LOG.info('Device is initialized now')
        except Exception as e:
            print("Exception received: %s" %e.message)
            os._exit(0)

    def close(self):
        self.evHandle.Unsubscribe()
        self.connected = False