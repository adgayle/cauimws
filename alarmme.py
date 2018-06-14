#!/usr/bin/env python
'''Example for opening an alarm using API in UIM'''
from __future__ import print_function
import logging
from ConfigParser import SafeConfigParser

import cauimws

def main():
    '''Opens UIM alarm via REST API'''
    # Init logging level
    logging.basicConfig(level=logging.DEBUG)

    # Get configuration data
    config = SafeConfigParser()
    config.read('conf\\config.ini')

    # Init the dict with UIM REST API information
    uim_ws = {}
    uim_ws['user'] = config.get('uim_ws', 'user')
    uim_ws['password'] = config.get('uim_ws', 'password')
    uim_ws['url'] = config.get('uim_ws', 'url')
    uim_ws['domain'] = config.get('uim_ws', 'domain')

    # Source of alarm
    source = 'source.example.org'
    # Alarm subsystem id if unsure use 1.1
    ss_id = '1.1'
    # Alarm suppression key 
    supp_key = 'suppression_key_01_test_alarm'
    # Alarm level e.g. clear, warning, minor, major, critical 
    level = 'warning'
    # Alarm message / text detail
    msg = 'This is our UIM API test alarm'

    # Open alarm
    cauimws.create_alarm(uim_ws, source, ss_id, supp_key, level, msg)


if __name__ == '__main__':
    main()
