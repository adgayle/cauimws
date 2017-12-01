#!/usr/bin/env python
'''Retrieves the CA UIM computer system id via the REST API
'''
from __future__ import print_function
import logging
from ConfigParser import SafeConfigParser

from cauimws import get_comp_sys_ids


def main():
    '''Retrieves the CA UIM computer system id via the REST API
    '''

    # Init logging level
    logging.basicConfig(level=logging.ERROR)

    # Get configuration data
    config = SafeConfigParser()
    config.read('conf\\config.ini')

    # Init the dict with UIM REST API information
    uim_ws = {}
    uim_ws['user'] = config.get('uim_ws', 'user')
    uim_ws['password'] = config.get('uim_ws', 'password')
    uim_ws['url'] = config.get('uim_ws', 'url')
    uim_ws['domain'] = config.get('uim_ws', 'domain')

    # Init list of computer system id(s)
    cs_id_list = []

    devices = ['server1', 'server2', 'server3', 'server4']
    for each_device in devices:
        if each_device:
            cs_ids = get_comp_sys_ids(uim_ws, each_device)
            for each_cs_id in cs_ids:
                cs_id_name_list = []
                cs_id_name_list.append(each_cs_id)
                cs_id_name_list.append(each_device)
                cs_id_list.append(tuple(cs_id_name_list))

    print(cs_id_list)



if __name__ == '__main__':
    main()
