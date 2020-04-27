import sqlite3
from sqlite3 import Error

from logs import logger

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        logger.error('error {0} occurred while creating connection to database'.format(e))

    return connection

def create_table():
    return 'CREATE TABLE IF NOT EXISTS ids ( id INTEGER NOT NULL, threshold INTEGER NOT NULL );'

def insert_id(id, threshold):
    return 'INSERT INTO ids (id, threshold) VALUES ({0}, {1});'.format(id, threshold)

def select_id(id):
    return 'SELECT id FROM ids WHERE id = {0}'.format(id)

def select_all():
    return 'SELECT * FROM ids'

def remove_id(id):
    return 'DELETE FROM ids WHERE id = {0}'.format(id)

def update_level(id, level):
    return 'UPDATE ids SET threshold = {1} WHERE id = {0}'.format(id, level)


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
    connection.close()