__author__ = "Amish Anand"
__copyright__ = "Copyright (c) 2016 Juniper Networks, Inc."

import logging

# Logging Parameters
DEFAULT_LOG_FILE_NAME = '/tmp/jetapp.log'
DEFAULT_LOG_LEVEL = logging.INFO

# Enable Logging to a file
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)s ] %(message)s"
logging.basicConfig(filename=DEFAULT_LOG_FILE_NAME, level=DEFAULT_LOG_LEVEL, format = FORMAT)
LOG = logging.getLogger(__name__)
