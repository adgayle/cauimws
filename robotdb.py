#!/usr/bin/env python
'''Methods for creating and storing robots and hubs in a sqlite db
'''
from __future__ import print_function
import logging
from sqlite3 import connect, Error


def create_db(db_file):
    '''Creates a sqlite database to store hub and robot relationship

    Args:
        db_file (string) the full path name of the database file

    Returns:
        True if successful, False if it fails
    '''

    drop_query = 'DROP TABLE IF EXISTS uim_robots_tbl'
    create_query = '''
        CREATE TABLE uim_robots_tbl (
            robot TEXT PRIMARY KEY,
            hub TEXT
        )
    '''

    result = False
    try:
        conn = connect(db_file)
        cursor = conn.cursor()
        cursor.execute(drop_query)
        conn.commit()
        cursor.execute(create_query)
        conn.commit()
        result = True

    except Error:
        logging.exception('Unable to create sqlite table for robots')

    if conn:
        conn.close()

    return result


def put_robots(db_file, hub, robots):
    '''Inserts rows for each hub robot combination into the database

    Args:
        db_file (string) the full path name of the database file
        hub (string) the name of the hub owning the robots
        robots (list) the robots that belong to the hub

    Returns:
        True if successful, False if it fails
    '''

    result = True
    try:
        conn = connect(db_file)
        cursor = conn.cursor()

        # Store robots assigned to hub in db
        for robot in robots:
            query = """
                INSERT INTO uim_robots_tbl (robot, hub)
                VALUES('{}', '{}')
                """.format(robot['name'], hub)
            logging.debug('The insert query is %s', query)
            try:
                cursor.execute(query)
                conn.commit()

            except Error:
                logging.exception(
                    'Unable to insert robot %s and hub %s',
                    robot['name'],
                    hub
                )
                result = False
    except Error:
        logging.exception('Unable to connect to SQLite DB %s', db_file)
        result = False

    if conn:
        conn.close()

    return result


def get_targets(db_file):
    '''Gets all the robots and the hubs they belong do'''
    results = []
    query = 'SELECT robot, hub FROM uim_robots_tbl'
    try:
        conn = connect(db_file)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
    except Error:
        logging.exception('Unable to query robots and hubs')

    if conn:
        conn.close()

    return results

def has_robot(db_file, hostname):
    '''Checks if hostname is in the robotsdb

    Args:
        db_file (string) the full path name of the database file
        hostname (string) The name of the machine from CMDB e.g. server1

    Returns:
        The row (list) with 0=hub, 1=robot if successful or None
    '''

    query = """
        SELECT hub, robot
        FROM uim_robots_tbl
        WHERE lower(robot) = '{}'""".format(hostname.lower())

    row = None
    try:
        conn = connect(db_file)
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()

    except Error:
        logging.exception(
            'Unable to query SQLite DB %s for hostname %s',
            db_file,
            hostname
        )

    if conn:
        conn.close()

    return row
