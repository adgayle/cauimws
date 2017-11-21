#!/usr/bin/env python
'''Finds open CA Unified Infrastructure Management Robot Inactive alarms
closing the ones for systems that are offline
'''
from __future__ import print_function
import logging
from os import system
from cauimws import get_alarms, get_hubs, remove_robot, acknowledge_alarm


def is_reachable(device, retries, ttl):
    '''Checks if device can be pinged on the network

    Args:
        device (string) machine name or IP address
        retries (number) of times to check
        ttl (number) timeout of each ping

    Returns:
        True if ping successful, False if not
    '''
    # Build and run the Windows ping command. Change according to operating system
    command = 'ping -n ' + str(retries) + ' -i ' + str(ttl) + ' ' + device + ' >nul 2>&1'
    response = system(command)

    # 0 means a successful ping response
    if response == 0:
        pingable = True
    else:
        pingable = False

    return pingable


def find_hub_robot(hubs, hub_name):
    '''Finds the name for the robot for a hub named hub_name

    Args:
        hubs (dict) of UIM hubs
        hub_name (string) name of UIM hub

    Returns:
        robot (string) hosting the hub with name hub_name
    '''
    robot = None

    # Search all the hubs by name to find the robot hosting our hub
    for hub in hubs:
        if hub['name'] == hub_name:
            robot = hub['robotName']
            logging.debug('Found robot %s for hub %s', robot, hub_name)
            break

    return robot


def main():
    '''Finds open CA Unified Infrastructure Management Robot Inactive alarms
    closing the ones for systems that are offline
    '''
    # Init logging level
    logging.basicConfig(level=logging.DEBUG)

    # Setup ping TTL and retry
    ttl = 300
    retry = 2

    # Setup alarm filter
    alarm_filter = {}
    alarm_filter['level'] = 5
    alarm_filter['probe'] = 'hub'
    alarm_filter['subsystem_id'] = '1.2.2'

    # Init the dict with UIM REST API information
    uim_ws = {}
    uim_ws['user'] = 'uim_web_service_user'
    uim_ws['password'] = 'uim_web_service_user_password'
    uim_ws['url'] = 'http://ump.ca.com/rest'
    uim_ws['domain'] = 'uim_domain'

    # Get a list of alarms matching the filter
    alarms = get_alarms(uim_ws, alarm_filter)
    for alarm in alarms:
        logging.info('%s --> %s', alarm['source'], alarm['message'])

        # Check to see if alarm source is online
        if is_reachable(alarm['source'], retry, ttl):
            logging.info('Device %s is online. Leaving alarm open', alarm['source'])
        else:
            logging.warning(
                'Robot %s is offline. Removing from hub and acknowledging alarm',
                alarm['robot'][0]
            )
            # Get a list of all the UIM hubs
            hubs = get_hubs(uim_ws)

            # Search the hubs by name to find the robot hosting our hub
            hub_robot = find_hub_robot(hubs, alarm['hub'][0])

            # Remove the offline robot from the hub so it stops checking it
            remove_robot(uim_ws, alarm['hub'][0], hub_robot, alarm['robot'][0])

            # Close the robot inactive alarm
            # --> Robot will join hub when it comes back online
            acknowledge_alarm(uim_ws, alarm['id'])


if __name__ == '__main__':
    main()
