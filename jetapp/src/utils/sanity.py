__author__ = "Amish Anand"
__copyright__ = "Copyright (c) 2015 Juniper Networks, Inc."

from utils.jetapplog import LOG
from jnpr.junos import Device
from lxml import etree

class Sanity(object):
    """
    Contains the sanity functions for the JET app
    """
    def __init__(self, dev):
        print("Sanity object initialized")
        print dev
        self._dev = dev

    def YangModulePresent(self):
        # Check if the YANG modules are present on the device
        try:
            pyez_client = Device(host=self._dev._host, user=self._dev._auth_user, password=self._dev._auth_pwd, gather_facts=False)
            pyez_client.open()
        except Exception as e:
            LOG.critical('Failed to connect to the device, exception: %s' %e.message)
            return
        try:
            result = pyez_client.rpc.get_system_yang_packages()
            pyez_client.close()
            xml_output = etree.tostring(result)
            if "ietf-inet-types.yang" in xml_output and "ietf-softwire.yang" in xml_output:
                LOG.info('Yang config is present in the device')
                return True
            else:
                LOG.info('Yang config is not present in the device')
                return False
        except Exception as e:
            LOG.critical('Yang config not present, exception = %s' %e.message)
            return False

    def NotificationConfigPresent(self):
        # Check if the commit notification config is present
        try:
            pyez_client = Device(host=self._dev._host, user=self._dev._auth_user, password=self._dev._auth_pwd, gather_facts=False)
            pyez_client.open()
        except Exception as e:
            LOG.critical('Failed to connect to the device, exception: %s' %e.message)
            return False
        try:
            json_query = """
                     <configuration>
                         <system>
                         <commit>
                         </commit>
                         </system>
                    </configuration>
            """
            result = pyez_client.rpc.get_config(filter_xml=etree.XML(json_query), options={'format': 'json'})
            pyez_client.close()
            LOG.info("Commit notifications configuration is already set")
            return True
        except Exception as e:
            LOG.critical('Commit notification is not present on the device')
            return False

    def CommitNotificationConfig(self):
        # Apply the commit notification config
        try:
            pyez_client = Device(host=self._dev._host, user=self._dev._auth_user, password=self._dev._auth_pwd, gather_facts=False)
            pyez_client.open()
        except Exception as e:
            LOG.critical('Failed to connect to the device, exception: %s' %e.message)
            return False
        try:
            from jnpr.junos.utils.config import Config
            cfg = Config(pyez_client)
            cfg.load("set system commit notification", format="set", merge=True)
            result = cfg.commit()
            LOG.info('Successfully set system commit configuration')
            pyez_client.close()
            return True
        except Exception as e:
            LOG.info('Failed to set the system commit notification: exception %s' %e.message)
            try:
                pyez_client.close()
            except:
                pass
            return False