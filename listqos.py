#!/usr/bin/env python
'''Using the current list of robots get the current value of
QOS_MEMORY_PHYSICAL_PERC for each when available
'''
from __future__ import print_function
import logging
from csv import writer

from cauimws import get_qos_targets, get_single_qos_value, get_qos_sources


def main():
    '''Using the current list of robots get the current value of
    QOS_MEMORY_PHYSICAL_PERC for each when available
    '''
    # Init logging level
    logging.basicConfig(level=logging.ERROR)

    # Init the dict with UIM REST API information
    uim_ws = {}
    uim_ws['user'] = 'uim_web_service_user'
    uim_ws['password'] = 'uim_web_service_user_password'
    uim_ws['url'] = 'http://ump.ca.com/rest'
    uim_ws['domain'] = 'uim_domain'

    # Init UIM origin to filter searches
    origin = 'list_of_origins'

    # Init UIM QOS to search
    qos = 'QOS_MEMORY_PHYSICAL_PERC'

    # Init UIM QOS start and end dates
    start = '201720110000'
    end = '201720112359'

    # Open the file to write the source and QOS value to
    with open('physMemValues.csv', 'wb') as phys_mem:
        wout = writer(phys_mem, delimiter=',')
        header = ['Server', 'Physical Memory Utilization %']
        wout.writerow(header)

        # Get a list of UIM sources that collect QOS_MEMORY_PHYSICAL_PERC
        qos_sources = get_qos_sources(uim_ws, qos)
        for qos_source in qos_sources:
            if qos_source['origin'][0] in origin:

                # Get a list of targets for the sources in our origin
                targets = get_qos_targets(uim_ws, qos_source['source'], qos)
                for target in targets:
                    # Get the QOS value
                    qos_value = get_single_qos_value(
                        uim_ws,
                        qos,
                        qos_source['source'],
                        target,
                        start,
                        end
                    )
                    if qos_value:
                        wout.writerow([qos_source['source'], qos_value])
                        break


if __name__ == '__main__':
    main()
