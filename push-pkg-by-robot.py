#!/usr/bin/env python
'''Pushes packages to robots
'''
from __future__ import print_function
import logging
import logging.handlers
from configparser import SafeConfigParser
from time import sleep

from robotdb import create_db, put_robots, has_robot
from cauimws import get_hubs, get_robots, get_probes, push_pkg


def main():
    '''Pushes packages to robots
    '''
    logging.basicConfig(
        filename='logs\\push-pkg-by-robot.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'
    )
    logging.info('Starting push-pkg-by-robot')
    config = SafeConfigParser()
    config.read('conf\\config-push-pkg-by-robot.ini')

    # Setup retry attempts and delay between tries
    retries = int(config.get('data', 'retries'))
    delay = int(config.get('data', 'delay'))

    # Setup UIM web services
    uim_ws = {}
    uim_ws['url'] = config.get('uimws', 'url')
    uim_ws['domain'] = config.get('uimws', 'domain')
    uim_ws['user'] = config.get('uimws', 'user')
    uim_ws['password'] = config.get('uimws', 'password')

    # Setup package and automated deployment engine
    package = config.get('uimws', 'package')
    ade = config.get('uimws', 'ade')

    # Count number of robots we push packages to
    times_pushed = 0

    # Setup hub exclusions for robots we are not going to touch
    excluded = config.get('uimws', 'exclude')

    # Setup sqlite robot database
    robotdb = config.get('data', 'robotdb')
    create_db(robotdb)

    # Get the hubs and retrieve the robots from each
    hubs = get_hubs(uim_ws)
    for hub in hubs:
        if hub['name'] not in excluded:
            robots = get_robots(uim_ws, hub['name'])

            # Populate robot DB with hub to robot relationship needed to push packages
            put_robots(robotdb, hub['name'], robots)

    with open('data\\targets.txt', 'rb') as targets, \
         open('reports\\norobot.txt', 'wb') as f_norobot, \
         open('reports\\pushed.txt', 'wb') as f_pushed:
        for target in targets:
            robot = target.strip().lower()

            logging.info('Processing %s', robot)
            found = has_robot(robotdb, robot)
            if found:
                # Found the robot and hub so pushing pushing package
                pushed = push_pkg(uim_ws, ade, package, found[0], found[1])
                attempts = 0
                while not pushed and attempts < retries:
                    sleep(delay)
                    pushed = push_pkg(uim_ws, ade, package, found[0], found[1])
                    attempts += 1

                if pushed:
                    f_pushed.write('{}\n'.format(robot))
                    times_pushed += 1
            else:
                f_norobot.write('{}\n'.format(robot))

    logging.info('Pushed %s package to %s robots', package, times_pushed)
    logging.info('End of push-pkg-by-robot')


if __name__ == '__main__':
    main()
