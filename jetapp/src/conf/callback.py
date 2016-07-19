__author__ = "Amish Anand"
__copyright__ = "Copyright (c) 2015 Juniper Networks, Inc."

from utils.jetapplog import LOG
from jnpr.junos import Device
from lxml import etree
from confGlobals import dispQ
import os

class SnabbCallback:
    def __init__(self, dev):
        self._dev = dev

    def __call__(self, message):
        global dispQ
        LOG.info("Inside Handle commit notifications")
        LOG.info("Received message: %s" %str(message))
        config_dict = message['commit-patch']['configuration']
        try:
            sw_present = False
            for keys in config_dict:
                if keys.endswith('softwire-config'):
                    sw_present = True
                    break
            if sw_present:
                # Push all the configuration into a new file
                try:
                    pyez_client = Device(host=self._dev._host, user=self._dev._auth_user, password=self._dev._auth_pwd, gather_facts=False)
                    pyez_client.open()
                except Exception as e:
                    LOG.critical('Failed to connect to the device, exception: %s' %e.message)
                    return
                try:
                    json_query = """
                                 <configuration>
                                     <softwire-config>
                                    </softwire-config>
                                </configuration>
                                """
                    result = pyez_client.rpc.get_config(filter_xml=etree.XML(json_query), options={'format': 'json'})
                    pyez_client.close()
                    LOG.info('Applied the pyez query, got this result: %s' %result)
                    config_dict = result["configuration"]["softwire-config"]
                    LOG.debug("Notification message contains the config %s" %(str(config_dict)))
                    dispQ.put(config_dict)
                except Exception as e:
                    LOG.info("The softwire-config was deleted by the user, purging all the config files")
                    config_dict = {'purge': 1}
                    dispQ.put(config_dict)
                return
            else:
                LOG.info("Softwire-config not present in the notification")

        except Exception as e:
            LOG.critical("Exception: %s" %e.message)
            LOG.info('Exiting the JET app')
            os._exit(1)
        return

