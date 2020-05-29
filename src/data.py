import sqlite3
from sqlite3 import Error

from logs import logger
from cf import check_users


class ids_handler:
    @staticmethod
    def create_table():
        return 'CREATE TABLE IF NOT EXISTS ids ( id INTEGER NOT NULL, handle TEXT )'

    @staticmethod
    def select_all():
        return 'SELECT * FROM ids'

    @staticmethod
    def select_id(id):
        return 'SELECT id FROM ids WHERE id = {0}'.format(id)

    @staticmethod
    def select_all_ids():
        return 'SELECT id FROM IDS'

    @staticmethod
    def insert_id(id):
        return 'INSERT INTO ids VALUES ({0}, NULL)'.format(id)

    @staticmethod
    def remove_id(id):
        return 'DELETE FROM ids WHERE id = {0}'.format(id)

    @staticmethod
    def select_handle(id, handle):
        return 'SELECT id, handle FROM ids WHERE id = {0} AND handle = "{1}"'.format(id, handle)

    @staticmethod
    def select_handles(id):
        return 'SELECT handle FROM ids WHERE id = {0}'.format(id)

    @staticmethod
    def insert_handle(id, handle):
        return 'INSERT INTO ids VALUES ({0}, "{1}")'.format(id, handle)    

    @staticmethod
    def remove_handle(id, handle):
        return 'DELETE FROM ids WHERE id = {0} AND handle = "{1}"'.format(id, handle)


class keys_handler:
    @staticmethod
    def create_table():
        return 'CREATE TABLE IF NOT EXISTS keys ( id INTEGER, open TEXT, secret TEXT )'
    
    @staticmethod
    def select_all():
        return 'SELECT * FROM keys'

    @staticmethod
    def insert_keys(id, open, secret):
        return 'INSERT INTO keys VALUES ({0}, "{1}", "{2}")'.format(id, open, secret)

    @staticmethod
    def select_keys(id):
        return 'SELECT open, secret FROM keys WHERE id = {0}'.format(id)
    
    @staticmethod
    def remove_keys(id):
        return 'DELETE FROM keys WHERE id = {0}'.format(id)
    
    @staticmethod
    def drop_table():
        return 'DROP TABLE keys'
    

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        logger.error('error {0} occurred while creating connection to database'.format(e))

    return connection

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
    execute_query(connection, ids_handler.create_table())
    execute_query(connection, keys_handler.create_table())
    
    #data = execute_read_query(connection, ids_handler.select_all())
    #for elem in data:
    #    if elem[1] != None and check_user(elem[1]) == 0:
    #        execute_query(connection, ids_handler.remove_handle(elem[0], elem[1]))

    connection.close()