#!/usr/bin/env python
'''Lists all the probes and their state in the CA UIM environment
'''
from __future__ import print_function
import logging
from csv import writer
from cauimws import get_hubs, get_robots, get_probes

def main():
    '''Lists all the probes and their state in the CA UIM environment
    '''
    # Init logging level
    logging.basicConfig(level=logging.ERROR)

    # Init the dict with UIM REST API information
    uim_ws = {}
    uim_ws['user'] = 'uim_web_service_user'
    uim_ws['password'] = 'uim_web_service_user_password'
    uim_ws['url'] = 'http://ump.ca.com/rest'
    uim_ws['domain'] = 'uim_domain'

    # Setup csv file for output
    with open('probesList.csv', 'wb') as probes_list:
        wout = writer(probes_list, delimiter=',')
        header = ['Hub', 'Robot', 'Probe', 'Status']
        wout.writerow(header)

        # Get the list of hubs from UIM
        hubs = get_hubs(uim_ws)
        for hub in hubs:

            # Get the list of robots assigned to hub
            robots = get_robots(uim_ws, hub['name'])
            for robot in robots:

                # Get the list of probes assigned to the robot
                probes = get_probes(uim_ws, hub['name'], robot['name'])
                if probes:
                    for probe in probes:
                        # Translate the probe state
                        if probe['active'].lower() == 'true':
                            state = 'Active'
                        else:
                            state = 'Inactive'
                        wout.writerow([hub['name'], robot['name'], probe['name'], state])
                else:
                    wout.writerow([hub['name'], robot['name'], '', ''])



if __name__ == '__main__':
    main()
