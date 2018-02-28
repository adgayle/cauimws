#!/usr/bin/env python
'''Sample code for placing things in maintenance mode with the UIM REST API
'''
from __future__ import print_function
import logging
from ConfigParser import SafeConfigParser
from datetime import datetime

from cauimws import create_mm_schedule, add_cs_to_mm_schedule, get_comp_sys_ids

def get_systems_list(filename, ws_info):
    '''Reads the list of systems to put in maintenance and returns their cs_ids in a list
    of strings

    Args:
        filename (string) path to file with systems to put in maintenance mode

    Returns:
        ["list of strings"]
    '''

    cs_ids = []
    with open(filename, 'r') as systems:
        comp_sys_name = systems.readline().strip()
        while comp_sys_name:
            logging.info('Processing %s', comp_sys_name)
            cs_id_list = get_comp_sys_ids(ws_info, comp_sys_name)
            for id in cs_id_list:
                cs_ids.append(id)
            comp_sys_name = systems.readline().strip()

    return cs_ids

def main():
    '''Sample code for placing things in maintenance mode with the UIM REST API
    '''
    # Init logging level
    logging.basicConfig(level=logging.DEBUG)

    # Set initial schedule values
    name = "March Windows Patching"
    desc = "March Windows Patching"
    # Date is March 3rd 2018 4:00 PM
    start_str = '2018-03-03-16-00-00'
    duration = 4
    timezone = 'America/New_York'

    # Convert string time to datetime
    start = datetime.strptime(start_str, '%Y-%m-%d-%H-%M-%S')

    # Get configuration data
    config = SafeConfigParser()
    config.read('conf\\config.ini')

    # Get filename with systems to put in maintenance mode
    systems_list_file = config.get('data', 'systems_list_file')

    # Init the dict with UIM REST API information
    uim_ws = {}
    uim_ws['user'] = config.get('uim_ws', 'user')
    uim_ws['password'] = config.get('uim_ws', 'password')
    uim_ws['url'] = config.get('uim_ws', 'url')
    uim_ws['domain'] = config.get('uim_ws', 'domain')
    uim_ws['pri_hub'] = config.get('uim_ws', 'primary_hub')
    uim_ws['mm_robot'] = config.get('uim_ws', 'mm_robot')

    # Create maintenance schedule
    schedule_id = create_mm_schedule(uim_ws, name, desc, start, duration, timezone)
    # Get the list of systems to put in maintenance mode and convert to cs_id list
    cs_ids = get_systems_list(systems_list_file, uim_ws)
    # Add the list of systems as cs_ids to the maintenance mode schedule
    if add_cs_to_mm_schedule(uim_ws, schedule_id, cs_ids):
        logging.info('Successfully add systems to maintenance')
    else:
        logging.critical('Failed to add systems to maintenance mode')


if __name__ == '__main__':
    main()