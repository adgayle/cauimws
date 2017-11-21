#!/usr/bin/env python
'''Functions for calling the CA Unified Infrastructure Management (UIM)
REST API
'''
from __future__ import print_function
import logging
from json import loads, dumps
from requests import get, post, put, ConnectionError
from requests.auth import HTTPBasicAuth

def get_hubs(ws_info):
    '''Obtains a list of hubs from the UIM domain

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/uim-infrastructure-calls#UIMInfrastructureCalls-GetListofHubs

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL

    Returns:
        (dict) containing list of UIM hubs
    '''
    url = ws_info['url'] + '/hubs'
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    params = {
        'inCurrentDomain': 'true'
    }

    results = loads('{}')
    try:
        response = get(
            url,
            auth=HTTPBasicAuth(
                ws_info['user'],
                ws_info['password']
            ),
            verify=False,
            headers=headers,
            params=params
        )
        logging.debug('Get hub response was %s', response.text)
        if response.status_code == 200:
            hubs = loads(response.text)
            results = hubs['hub']
        else:
            logging.error('Failed to get hubs')

    except ConnectionError:
        logging.exception('Failed to call UIM hub API')

    return results


def get_robots(ws_info, hub):
    '''Obtains a list of robots assigned to the UIM hub

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/uim-infrastructure-calls#UIMInfrastructureCalls-GetListofRobots

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        hub (string) name of the UIM hub

    Returns:
        (dict) containing list of UIM robots
    '''
    url = ws_info['url'] + '/hubs/' + ws_info['domain'] + '/' + hub + '/' + 'robots'
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    params = {
        'inCurrentDomain': 'true'
    }

    results = loads('{}')
    try:
        response = get(
            url,
            auth=HTTPBasicAuth(
                ws_info['user'],
                ws_info['password']
            ),
            verify=False,
            headers=headers,
            params=params
        )
        logging.debug('Get robot response was %s', response.text)
        if response.status_code == 200:
            robots = loads(response.text)
            results = robots['robot']
        else:
            logging.error('Failed get robots')

    except ConnectionError:
        logging.exception('Failed to call UIM robots API')

    return results


def get_probes(ws_info, hub, robot):
    '''Obtain a list of probes on a UIM robot

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/uim-infrastructure-calls#UIMInfrastructureCalls-GetRobotDetails

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        hub (string) name of the UIM hub
        robot (string) name of the UIM robot assigned to hub

    Returns:
        (dict) containing list of UIM probes
    '''
    url = ws_info['url'] + '/hubs/' + ws_info['domain'] + '/' + hub + '/' + robot
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }

    results = loads('{}')
    try:
        response = get(
            url,
            auth=HTTPBasicAuth(
                ws_info['user'],
                ws_info['password']
            ),
            verify=False,
            headers=headers
        )
        if response.status_code == 200:
            probes = loads(response.text)
            results = probes['probes']
        else:
            logging.error('Failed to get probes')

    except ConnectionError:
        logging.exception('Failed to call UIM probes API')

    except KeyError:
        logging.exception('No probes returned from call UIM probes API')

    return results


def get_alarms(ws_info, alarm_filter):
    '''Obtains all a list of UIM alarms matching filter

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/alarm-calls#AlarmCalls-GetAlarmList(Filtered)

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        filter (dict) containing
            level (number) representing alarm severity 0, 1, 2, 3, 4, 5 = critical
            probe (string) causing the alarm
            subsystem_id (string) alarm subsystem id
    Returns:
        (dict) of matching alarms
    '''
    url = ws_info['url'] + '/alarms'
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }

    results = loads('{}')
    try:
        response = post(
            url,
            auth=HTTPBasicAuth(
                ws_info['user'],
                ws_info['password']
            ),
            verify=False,
            headers=headers,
            data=dumps(alarm_filter)
        )
        logging.debug('Get alarms response was %s', response.text)
        if response.status_code == 200:
            alarms = loads(response.text)
            results = alarms['alarm']
        else:
            logging.error('Failed to get alarms')

    except ConnectionError:
        logging.exception('Failed to call UIM alarm API')

    except KeyError:
        logging.exception('No alarms returned from filtered alarm API call')

    return results


def remove_robot(ws_info, hub, hub_robot, robot):
    '''Removes a robot from the UIM hub using the removerobot callback

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/probe-calls#ProbeCalls-InvokeCallback

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        hub (string) name of the UIM hub
        robot (string) name of the UIM robot assigned to hub
        hub_robot (string) name of the UIM robot running the hub

    Returns:
        True if successfully in removing the robot, False if not
    '''
    url = ws_info['url'] + '/probe/' + ws_info['domain'] + '/' + hub + '/' + \
        hub_robot + '/hub/callback/removerobot'
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    data = {
        'parameters' : {
            'name': 'name',
            'type': 'string',
            'value': ''
        }
    }
    data['parameters']['value'] = robot

    result = False
    try:
        response = post(
            url,
            auth=HTTPBasicAuth(
                ws_info['user'],
                ws_info['password']
            ),
            verify=False,
            headers=headers,
            data=dumps(data)
        )
        logging.debug('The response from callback removerobot was %s', response.text)
        if response.status_code == 200:
            result = True
        else:
            logging.error('Failed to remove robot %s', robot)

    except ConnectionError:
        logging.exception('Failed to callback removerobot API')

    return result


def acknowledge_alarm(ws_info, alarm_id):
    '''Acknowledges / closes the UIM alarm with alarm_id

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/alarm-calls#AlarmCalls-UpdateanAlarm(Acknowledge)

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL

    Returns
        True if successful, False if not
    '''
    url = ws_info['url'] + '/alarms/' + alarm_id + '/ack'
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }

    result = False
    try:
        response = put(
            url,
            auth=HTTPBasicAuth(
                ws_info['user'],
                ws_info['password']
            ),
            verify=False,
            headers=headers
        )
        if response.status_code == 204:
            logging.info('successfully close alarm with id %s', alarm_id)
            result = True

    except ConnectionError:
        logging.exception('Failed to call acknowledge alarm API for %s', alarm_id)

    return result


def get_qos_targets(ws_info, source, qos):
    '''Returns a list of targets for a given source and QOS

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/qos-calls#QoSCalls-GetTargetsforQoS-NameandSource

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
        qos (string) name of the QOS metrics to retrieve
        source (string) name of the device to get targets for

    Returns:
        targets (list) of targets for QOS on source

    '''
    url = ws_info['url'] + '/qos/targets/' + qos + '/' + source
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    targets = []

    try:
        response = get(
            url,
            auth=HTTPBasicAuth(
                ws_info['user'],
                ws_info['password']
            ),
            verify=False,
            headers=headers
        )
        logging.debug(
            'The response for get targets of QOS %s for source %s was %s',
            qos,
            source,
            response.text
        )
        if response.status_code == 200 and not response.text == '{}':
            results = loads(response.text)
            targets = results['target']
    except ConnectionError:
        logging.exception(
            'Failed API call to retrieve list of targets for qos %s from source %s',
            qos,
            source
        )

    return targets


def get_single_qos_value(ws_info, qos, source, target, start, end):
    '''Returns a single qos data value between the start and end times

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/qos-calls#QoSCalls-GetRawQoSData

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
        qos (string) name of the QOS metrics to retrieve
        source (string) name of the device to get targets for
        target (string) UIM target or component to retrieve the QOS data for
        start (string) beginning of time to retrieve qos format yyyyddMMHHmm
        end (string) end of time to retrieve qos format yyyyddMMHHmm
    Returns:
        value (number) single data value if found or None
    '''
    url = ws_info['url'] + '/qos/data/name/' + qos + \
        '/' + source + '/' + target + '/' + start + '/' + \
        end + '/1'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    value = None
    try:
        response = get(
            url,
            auth=HTTPBasicAuth(
                ws_info['user'],
                ws_info['password']
            ),
            verify=False,
            headers=headers
        )

        logging.debug(
            'The response for get %s QOS for %s device was %s',
            qos,
            source,
            response.text
        )
        if response.status_code == 200 and not response.text == '{}':
            result = loads(response.text)
            value = result['data'][0]['samplevalue']

    except ConnectionError:
        logging.exception(
            'Failed to call API to get QOS value for %s QOS with %s source',
            qos,
            source
        )

    return value


def get_qos_sources(ws_info, qos):
    '''Returns a list of sources for a given QOS name

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/qos-calls#QoSCalls-GetSourcesforQoS-Name

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
        qos (string) name of the QOS metrics to retrieve

    Returns:
        sources (list) of targets for QOS on source

    '''
    url = ws_info['url'] + '/qos/sources/' + qos
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    sources = []
    try:
        response = get(
            url,
            auth=HTTPBasicAuth(
                ws_info['user'],
                ws_info['password']
            ),
            verify=False,
            headers=headers
        )
        logging.debug('The response for get QOS sources was %s', response.text)
        if response.status_code == 200 and not response.text == '{}':
            results = loads(response.text)
            sources = results['qos-source']

    except ConnectionError:
        logging.exception('Failed to call API to get sources for %s QOS', qos)

    return sources
