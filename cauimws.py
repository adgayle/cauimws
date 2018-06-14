#!/usr/bin/env python
'''Functions for calling the CA Unified Infrastructure Management (UIM)
REST API
'''
from __future__ import print_function
import logging
from socket import gethostbyname, gaierror
from json import loads, dumps
from re import search
from requests import get, post, put, delete, ConnectionError, Timeout
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


def _get_ip(device):
    '''Obtains the IP address of device

    Args:
        device (string) name to get an IP address for

    Returns:
        ip_addr (string) ip address of device or None on failure
    '''

    ip_addr = None
    try:
        ip_addr = gethostbyname(device)
        logging.debug('IP address for %s is %s', device, ip_addr)
    except gaierror:
        logging.exception('Failed to call gethostbyname for %s', device)

    return ip_addr


def get_comp_sys_ids(ws_info, device):
    '''Obtains the computer system id for the device from the UIM API

    API Links:
        https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/computer-system-calls#ComputerSystemCalls-GetComputerSystemDetails(UsingtheIPAddress)
        https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/computer-system-calls#ComputerSystemCalls-GetComputerSystemDetails(UsingtheCSName)

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
        device (string) to get the computer system id(s) for

    Returns:
        cs_id (list) of the computer system id(s)
    '''
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    cs_id = []
    ip_addr = _get_ip(device)
    if ip_addr:
        url = ws_info['url'] + '/computer_systems/cs_ip/' + ip_addr

        try:
            response = get(
                url,
                auth=HTTPBasicAuth(
                    ws_info['user'],
                    ws_info['password']
                ),
                verify=False,
                headers=headers)

            logging.debug(
                'The response from the get computer system id by IP was %s',
                response.text
            )
            if response.status_code == 200:
                results = loads(response.text)

                # UIM sometimes has duplicate devices not correlated by discovery_server
                for computer_system in results['computer_system']:
                    cs_id.append(computer_system['cs_id'])

                logging.info(
                    'Successfully got the computer system id for %s by IP as %s',
                    device,
                    str(cs_id))
            else:
                logging.warning(
                    'Failed to get computer system id for %s. Response code was %s',
                    device,
                    response.status_code
                )

        except ConnectionError:
            logging.exception('Failed to call UIM computer system id by IP API')

        except KeyError:
            logging.exception('No computer systems found by IP for name %s', device)
    else:
        url = ws_info['url'] + '/computer_systems/cs_name/' + device

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
                'The response from the get computer system id by name was %s',
                response.text
            )
            if response.status_code == 200:
                results = loads(response.text)
                for computer_system in results['computer_system']:
                    cs_id.append(computer_system['cs_id'])

                logging.info(
                    'Successfully got the computer system id for %s by name as %s',
                    device,
                    str(cs_id)
                )

            else:
                logging.warning(
                    'Failed to get computer system id for %s by name. Response code was %s',
                    device,
                    response.status_code
                )

        except ConnectionError:
            logging.exception('Failed to call UIM computer system id by name API')

        except KeyError:
            logging.exception('No computer systems found by name for name %s', device)

    return cs_id


def nis_cache_clean(ws_info, robot_address):
    '''Clears the robot niscache using the _nis_cache_clean callback

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/probe-calls#ProbeCalls-InvokeCallback

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        robot_address (string) of the address to the UIM robot

    Returns:
        True if successfull in running cleaning the nis cache, False if not
    '''
    url = ws_info['url'] + '/probe' + robot_address + '/controller/callback/_nis_cache_clean'
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    data = {
        'parameters' : {
            'name': 'robot',
            'type': 'string',
            'value': ''
        }
    }
    found = search(r'/.+/.+/(.+)$', robot_address)
    robot = found.group(1)
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
        logging.debug('The response from callback _nis_cache_clean was %s', response.text)
        if response.status_code == 200:
            result = True
        else:
            logging.error('Failed to clean nis cache for robot %s', robot_address)

    except ConnectionError:
        logging.exception('Failed to callback _nis_cache_clean API')

    return result


def reset_device_id_and_restart(ws_info, robot_address):
    '''Resets the robot device id and restarts the robot

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/probe-calls#ProbeCalls-InvokeCallback

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        robot_address (string) of the address to the UIM robot

    Returns:
        True if successfull in reseting the device id and restarting, False if not
    '''
    url = ws_info['url'] + '/probe' + robot_address + \
        '/controller/callback/_reset_device_id_and_restart'
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    data = {
        'parameters' : {
            'name': 'robot',
            'type': 'string',
            'value': ''
        }
    }

    found = search(r'/.+/.+/(.+)$', robot_address)
    robot = found.group(1)
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
        logging.debug(
            'The response from callback _reset_device_id_and_restart was %s',
            response.text
        )
        if response.status_code == 200:
            result = True
        else:
            logging.error(
                'Failed to reset device id and restart for robot %s',
                robot_address
            )

    except ConnectionError:
        logging.exception('Failed to callback _reset_device_id_and_restart API')

    return result


def push_pkg(ws_info, ade, package, hub, robot):
    '''Pushes package to robot

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/probe-calls#ProbeCalls-InvokeCallback

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        ade (string) UIM address of the robot with the ADE probe
        package (string) name of package to deploy
        hub (string) name of hub the robot target belongs to
        robot (string) name of robot to deliver the package to

    Returns:
        True if job initiated successfully, False otherwise
    '''
    robot_address = '/' + ws_info['domain'] + '/' + hub + '/' + robot
    url = ws_info['url'] + '/probe' + ade \
        + '/automated_deployment_engine/callback/deploy_probe'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'parameters': [
            {'name': 'robot', 'type': 'string', 'value': ''},
            {'name': 'package', 'type': 'string', 'value': ''}
        ]
    }
    data['parameters'][0]['value'] = robot_address
    data['parameters'][1]['value'] = package

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
        logging.debug('The ADE package deploy response %s', response.text)
        if response.status_code == 200:
            result = True
        else:
            logging.error(
                'Failed to make deploy probe call for package %s to robot %s',
                package,
                robot
            )
    except ConnectionError:
        logging.exception('Failed to call deploy probe API callback')

    return result


def create_contact(ws_info, contact_data):
    '''    Use the CA UIM Web Services cauim_ws to create a new contact based on contact_data

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/contact-calls#ContactCalls-CreateaNewContact

    Args:
        ws_info (list) of CA UIM Web Services location and credentials
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        contact_data (list) of account contact information
            accountId (integer) account id as retrieved from the UIM database
            acl (string) UIM account contact ACL
            loginName (string) user login name
            firstName (string) user first name
            lastName (string) user last name
            email (string) address for the user
            password (string) user password for account contact user


    Returns:
        Contact ID of the user created or None on failure
    '''

    url = ws_info['url'] + '/contacts'
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'}

    contact_id = None
    try:
        response = post(
            url, 
            auth=HTTPBasicAuth(ws_info['user'], ws_info['password']),
            verify=False,
            headers=headers,
            data=dumps(contact_data)
        )

        if response.status_code == 200:
            json_returned = loads(response.text)
            contact_id = json_returned['contactId']
        else:
            logging.warning(
                'Unable to create contact %s, failed with status code %s',
                contact_data['loginName'],
                response.status_code
            )

    except ConnectionError:
        logging.exception('Failed to call API to create contact %s', contact_data['loginName'])
    except KeyError:
        logging.exception('No contact id was returned for creation of %s', contact_data['loginName'])

    return contact_id


def remove_mm_schedule(ws_info, schedule_id, uim_ws_mm_probe):
    '''Deletes a UIM maintenance schedule

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/maintenance-calls#MaintenanceCalls-DeleteaSchedule

    Args:
        ws_info (list) of CA UIM Web Services location and credentials
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        schedule_id (integer as string) id of the schedule to remove
        uim_ws_mm_probe (string) http path to maintenance mode probe

    Returns:
        Nothing
    '''

    try:
        mm_del_schedule_url = uim_ws_mm_probe + '/delete_schedule/' + schedule_id
        mm_del_resp = delete(
            mm_del_schedule_url,
            auth=HTTPBasicAuth(ws_info['user'], ws_info['password']),
            verify=False,
            timeout=30
        )
        if mm_del_resp.status_code == 204:
            logging.info('Successfully deleted schedule id: %s', schedule_id)
        else:
            logging.error(
                'Failed to delete schedule. URL called was %s status code was %s',
                mm_del_schedule_url,
                mm_del_resp.status_code
            )

    except ConnectionError:
        logging.exception('Failed to call delete schedule API.')
    except Timeout:
        logging.exception('Timed out waiting for delete maintenance schedule')

    return


def create_group(ws_info, pgrp_id, grp_name, grp_desc, grp_type):
    '''Create a group using the UIM web services API

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/group-resource-calls#GroupResourceCalls-CreateaStaticGroup

    Args:
        ws_info (list) of CA UIM Web Services location and credentials
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        pgrp_id (integer) group id of the parent to the new group
        grp_name (string) name of the new group
        grp_desc (string) description for the new group
        grp_type (integer) either a dynamic, static (0) or container group

    Returns:
        If successful the group id for the new group
        If unsucessful None is returned
    '''

    grp_id = None
    url = ws_info['url'] + '/group'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {}
    data['groupType'] = str(grp_type)
    data['parentGroupId'] = str(pgrp_id)
    data['groupName'] = grp_name
    if grp_desc is None or grp_desc == "":
        data['desc'] = grp_name
    else:
        data['desc'] = grp_desc

    try:
        response = post(
            url,
            auth=HTTPBasicAuth(ws_info['user'], ws_info['password']),
            verify=False,
            headers=headers,
            data=dumps(data)
        )

        logging.debug(
            'The response from the group creation was %s',
            response.text
        )
        if response.status_code == 200:
            json_resp = loads(response.text)
            grp_id = json_resp['groupId']
            logging.info(
                'Successfully created group %s with group id %s',
                grp_name,
                grp_id
            )
        else:
            logging.error(
                'Failed to connect to UIM API to create group with status code %s',
                response.status_code
            )
    except ConnectionError:
        logging.exception(
            'Failed to call the UIM API to create the group %s',
            grp_name
        )

    return grp_id


def add_grp_member(ws_info, grp_id, new_mem):
    '''Adds a new member to the group with id specified

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/group-resource-calls#GroupResourceCalls-AddGroupMembers

    Args:
        ws_info (list) of CA UIM Web Services location and credentials
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        grp_id (integer) id of the group we are adding the member to
        new_mem (integer) cs_id of the new member to add

    Returns:
        True if successful
        False if it fails
    '''

    logging.info('Adding %s to group %s', new_mem, grp_id)
    url = ws_info['url'] + '/group/members/' + str(grp_id)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'}
    data = {}
    data['cs'] = new_mem

    result = False

    try:
        response = post(
            url,
            auth=HTTPBasicAuth(ws_info['user'], ws_info['password']),
            verify=False,
            headers=headers,
            data=dumps(data)
        )

        logging.debug(
            'The response from the add group members was %s',
            response.text
        )
        if response.status_code == 204:
            logging.info(
                'Successfully added members to groupid %s', 
                grp_id
            )
            result = True
        else:
            logging.error(
                'Failed to connect to UIM API to add members to group %s, status code %s',
                grp_id,
                response.status_code
        )

    except ConnectionError:
        logging.exception(
            'Failed to connect to UIM API to add device %s to group id %s',
            new_mem,
            grp_id
    )

    return result


def group_exists(ws_info, grp_name):
    """Check if the group with a name already exists

    Args:
        ws_info (list) of CA UIM Web Services location and credentials
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        grp_name (string) name of the group we are checking if exists

    Returns:
        If the group exists the group id
        If the group does not exists or other failure None
    """

    url = ws_info['url'] + '/group/' + grp_name + '/exists'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'}
    grp_id = None
    try:
        response = get(
            url,
            auth=HTTPBasicAuth(ws_info['user'], ws_info['password']),
            verify=False,
            headers=headers
        )

        logging.debug(
            'The response from the group exists by name was %s',
            response.text
        )
        if response.status_code == 200:
            data = loads(response.text)
            grp_id = data['group']['groupId']
            logging.info(
                'Successfully got the group id for %s by name as %s',
                grp_name,
                grp_id
            )
        else:
            logging.warning(
                'Failed to check if group %s exists. Response code was %s',
                grp_name,
                response.status_code
            )
    except ConnectionError:
        logging.exception('Group exists API call failure with URL %s', url)

    return grp_id


def os_info(ws_info, hub, robot):
    '''Returns robot minor OS

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/probe-calls#ProbeCalls-InvokeCallback

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        hub (string) name of hub the robot target belongs to
        robot (string) name of robot to deliver the package to

    Returns:
        Robot OS e.g. Windows or Linux
    '''
    robot_address = '/' + ws_info['domain'] + '/' + hub + '/' + robot
    url = ws_info['url'] + '/probe' + robot_address \
        + '/controller/callback/os_info'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    data = {}
    oper_sys = None
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
        logging.debug('The os_info response %s', response.text)
        if response.status_code == 200:
            results = loads(response.text)
            oper_sys = results['entry'][0]['value']['$']
        else:
            logging.error('Failed to make os_info call for %s', robot_address)
    except ConnectionError:
        logging.exception('Failed to call os_info probe API callback')

    return oper_sys

def is_process_running(ws_info, hub, robot, process):
    '''Returns true if process is running on robot

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/probe-calls#ProbeCalls-InvokeCallback

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        hub (string) name of hub the robot target belongs to
        robot (string) name of robot to deliver the package to
        process (string) name of process to search for

    Returns:
        True if process is found, False otherwise
    '''
    robot_address = '/' + ws_info['domain'] + '/' + hub + '/' + robot
    url = ws_info['url'] + '/probe' + robot_address \
        + '/processes/callback/list_processes'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    data = {
        'parameters': [
            {'name': 'proc', 'type': 'string', 'value': ''}
        ]
    }
    data['parameters'][0]['value'] = process
    running = False
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
        logging.debug('The list_processes response %s', response.text)
        if response.status_code == 200:
            if process in response.text:
                running = True
        else:
            logging.error('Failed to make list_processes call for %s', robot_address)
    except ConnectionError:
        logging.exception('Failed to call list_processes probe API callback')

    return running


def set_custom(ws_info, nimid, attr):
    '''Set custom_2..5 in the UIM alarm

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/alarm-calls#AlarmCalls-CreateaCustomAlarmProperty

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        nimid (string) alarm id from UIM console or DB
        attr (dict) of alarm_property
            custom_1..5 (string) acts as the key each with a value to populate
    Returns:
        True if successful, False if fails    
    '''
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    url = ws_info['url'] + '/alarms/' + nimid + '/set_custom_property'

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
            data=dumps(attr)
        )
        logging.debug('The response from set_custom_property was %s', response.text)
        if response.status_code == 204:
            result = True

    except ConnectionError:
        logging.exception('Failed to call set_custom_property')

    return result

def assign_alarm(ws_info, nimid, assignee):
    '''Assign alarm
 
    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/alarm-calls#AlarmCalls-UpdateanAlarm(Assign)

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        nimid (string) alarm id from UIM console or DB
        assignee (string) user id assigning alarm to

    Returns:
        True if successful, False if fails

    '''
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }
    url = ws_info['url'] + '/alarms/' + nimid + '/assign/' + assignee

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
            result = True

    except ConnectionError:
        logging.exception('Failed to call assign')

    return result


def add_group_account(ws_info, grp_id, acc_id):
    '''Adds a UIM account to the group specified as grp_id

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        grp_id (string) containing the UIM group id
        acc_id (integer) containing the UIM account to assign to the group
    Returns:
        Nothing
    '''
    url = ws_info['url'] + '/group/accounts/' + grp_id
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    data = {'groupAccount': [1]}
    data['groupAccount'][0] = acc_id

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
        logging.debug('The status code from the group account update %s', response.status_code)
        if response.status_code == 204:
            logging.debug(
                'Successfully updated group %s with account %s',
                grp_id,
                acc_id
            )
        else:
            logging.warning(
                'Failed to update group %s with account %s',
                grp_id,
                acc_id
            )
    except ConnectionError:
        logging.exception('Connection error to UIM REST API')


def create_mm_schedule(ws_info, name, desc, start, duration, t_zone):
    '''Creates a maintenance mode schedule

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/maintenance-calls#MaintenanceCalls-CreateaSchedule

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
            pri_hub (string) UIM primary hub name (case sensitive)
            mm_robot (string) name of robot hosting maintenance_mode probe (case sensitive)
        name (string) schedule name
        desc (string) schedule description
        start (datetime)
        duration (integer) in hours
        t_zone (string) timezone to use
        acc_id (integer) the account id from UIM

    Returns:
        schedule_id if successful
        None on failure
    '''
    schedule = {}
    schedule['name'] = name
    schedule['description'] = desc
    schedule['start_date_time'] = {}
    schedule['start_date_time']['year'] = start.strftime('%Y')
    schedule['start_date_time']['month'] = start.strftime('%m')
    schedule['start_date_time']['day'] = start.strftime('%d')
    schedule['start_date_time']['timestamp'] = {}
    schedule['start_date_time']['timestamp']['hours'] = start.strftime('%H')
    schedule['start_date_time']['timestamp']['minutes'] = start.strftime('%M')
    schedule['start_date_time']['timestamp']['seconds'] = start.strftime('%S')
    schedule['end_time'] = {}
    schedule['end_time']['type'] = 'duration'
    schedule['end_time']['end_date_time'] = {}
    schedule['end_time']['end_date_time']['month'] = ''
    schedule['end_time']['end_date_time']['day'] = ''
    schedule['end_time']['end_date_time']['year'] = ''
    schedule['end_time']['end_date_time']['timestamp'] = {}
    schedule['end_time']['end_date_time']['timestamp']['hours'] = ''
    schedule['end_time']['end_date_time']['timestamp']['minutes'] = ''
    schedule['end_time']['end_date_time']['timestamp']['seconds'] = ''
    schedule['end_time']['duration'] = {}
    schedule['end_time']['duration']['hours'] = str(duration)
    schedule['end_time']['duration']['minutes'] = ''
    schedule['end_time']['duration']['seconds'] = ''
    schedule['account_id'] = ''
    schedule['recurrence_pattern'] = ''
    schedule['recurrence_period'] = ''
    schedule['recurrence_days_of_the_week'] = ''
    schedule['recurrence_day_of_the_month'] = ''
    schedule['recurrence_instance'] = ''
    schedule['recurrence_end_date_time']= {}
    schedule['recurrence_end_date_time']['month'] = ''
    schedule['recurrence_end_date_time']['day'] = ''
    schedule['recurrence_end_date_time']['year'] = ''
    schedule['recurrence_end_date_time']['timestamp'] = {}
    schedule['recurrence_end_date_time']['timestamp']['hours'] = ''
    schedule['recurrence_end_date_time']['timestamp']['minutes'] = ''
    schedule['recurrence_end_date_time']['timestamp']['seconds'] = ''
    schedule['timezone'] = t_zone

    url = ws_info['url'] + '/maintenance_mode/' + ws_info['domain'] + '/' + \
          ws_info['pri_hub'] + '/' + ws_info['mm_robot'] + '/add_schedule'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
        
    schedule_id = None
    try:
        response = post(
            url,
            auth=HTTPBasicAuth(
                ws_info['user'],
                ws_info['password']
            ),
            verify=False,
            headers=headers,
            data=dumps(schedule)
        )
        logging.debug('The status code from the create mm schedule call was %s', response.status_code)
        if response.status_code == 200:
            logging.debug('Successfully created maintenance schedule %s', name)
            results = loads(response.text)
            schedule_id = results['schedule_id']
        else:
            logging.warning('Failed to create maintenance schedule %s', name)
    except ConnectionError:
        logging.exception('Connection error to UIM REST API for maintenance schedule creation')

    except Timeout:
        logging.exception('Timeout error creating maintenance schedule')

    return schedule_id


def add_cs_to_mm_schedule(ws_info, schedule_id, cs_ids):
    '''Add computer systems to a maintenance mode schedule

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/maintenance-calls#MaintenanceCalls-AddComputerSystemstoaSchedule

    Args:
        ws_info (dict) containing
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
            pri_hub (string) UIM primary hub name (case sensitive)
            mm_robot (string) name of robot hosting maintenance_mode probe (case sensitive)
        schedule_id (integer) schedule id of the maintenance schedule
        cs_id (list of strings) the cs_id of the devices to put in maintenance mode

    Returns:
        True if successful
        False on failure
    '''
    url = ws_info['url'] + '/maintenance_mode/' + ws_info['domain'] + '/' + \
          ws_info['pri_hub'] + '/' + ws_info['mm_robot'] + '/add_computer_systems_to_schedule/' + \
          str(schedule_id)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {}
    data['cs'] = cs_ids
    logging.debug('List of systems to put in maintenance mode %s', data)
        
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
        logging.debug('The status code from the add computers to mm schedule call was %s', response.status_code)
        if response.status_code == 204:
            logging.debug('Successfully added computers to maintenance schedule %s', schedule_id)
            result = True
        else:
            logging.warning('Failed to add computers to maintenance schedule %s', schedule_id)
    except ConnectionError:
        logging.exception('Connection error to UIM REST API to add computers to maintenance schedule')

    except Timeout:
        logging.exception('Timeout error to add computers to maintenance schedule')

    return result


def create_alarm(ws_info, source, ss_id, supp_key, level, msg):
    '''Generates an alarm from source with ss_id, supp_key and severity (level)

    API Link: https://docops.ca.com/ca-unified-infrastructure-management-probes/ga/en/probe-development-tools/restful-web-services/call-reference/alarm-calls#AlarmCalls-CreateanAlarm

    Args:
        ws_info (dict) UIM web services connection information
            user (string) UIM user with web service access
            password (string) UIM user password
            url (string) UIM REST API URL
            domain (string) UIM domain name
        source (string) impacted configuration item of alarm
        ss_id (string) UIM alarm subsystem id
        supp_key (string) UIM alarm suppression key
        level (string) UIM alarm level
        msg (string) text of the new alarm

    Returns:
        True if successful, False if it failed
    '''

    url = ws_info['url'] + '/alarms/createAlarm'
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json'
    }

    severity = {
        'clear': '0',
        'info': '1',
        'warning': '2',
        'minor': '3',
        'major': '4',
        'critical': '5'
    }

    data = {}
    data['level'] = severity[level]
    data['message'] = msg
    data['source'] = source
    data['subsystemId'] = ss_id
    data['suppressionKey'] = supp_key
    data['severity'] = level
    result = False

    try:
        resp = post(
            url,
            auth=HTTPBasicAuth(
                ws_info['user'],
                ws_info['password']
            ),
            verify=False,
            timeout=30,
            headers=headers,
            data=dumps(data)
        )
        logging.debug('The response from the createAlarm API was %s', resp.status_code)
        if resp.status_code == 204:
            result = True

    except ConnectionError:
        logging.exception(
            'Failed to call createAlarm API for source %s with msg %s',
            source, msg
        )
    except Timeout:
        logging.exception('Timeout error to add computers to maintenance schedule')

    return result
