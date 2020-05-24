import sqlite3
from sqlite3 import Error

from logs import logger
from util import check_user

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        logger.error('error {0} occurred while creating connection to database'.format(e))

    return connection

def create_table():
    return 'CREATE TABLE IF NOT EXISTS ids ( id INTEGER NOT NULL, handle TEXT )'

def select_all():
    return 'SELECT * FROM ids'

def select_id(id):
    return 'SELECT id FROM ids WHERE id = {0}'.format(id)

def select_all_ids():
    return 'SELECT id FROM IDS'

def insert_id(id):
    return 'INSERT INTO ids VALUES ({0}, NULL)'.format(id)

def remove_id(id):
    return 'DELETE FROM ids WHERE id = {0}'.format(id)

def select_handle(id, handle):
    return 'SELECT id, handle FROM ids WHERE id = {0} AND handle = "{1}"'.format(id, handle)

def select_handles(id):
    return 'SELECT handle FROM ids WHERE id = {0}'.format(id)

def insert_handle(id, handle):
    return 'INSERT INTO ids VALUES ({0}, "{1}")'.format(id, handle)    

def remove_handle(id, handle):
    return 'DELETE FROM ids WHERE id = {0} AND handle = "{1}"'.format(id, handle)

def execute_query(connection, query):
    try:
        connection.cursor().execute(query)
        connection.commit()
    except Error as e:
        logger.error('error {0} occurred while processing query; query = {1}'.format(e, query))

def execute_read_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        logger.error('error {0} occurred while reading; query = {1}'.format(e, query))

if __name__ == '__main__':
    connection = create_connection('list.db')
    execute_query(connection, create_table())

    for elem in data:
        if elem[1] != None and check_user(elem[1]) == 0:
            execute_query(connection, remove_handle(elem[0], elem[1]))

    connection.close()