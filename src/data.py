import psycopg2

from logs import logger
from var import password
from var import dbname


class ids_handler:
    """
    id, handle
    """
    @staticmethod
    def create_table():
        return "CREATE TABLE IF NOT EXISTS ids ( id INTEGER NOT NULL, handle TEXT )"

    @staticmethod
    def select_all():
        return "SELECT * FROM ids"

    @staticmethod
    def select_all_ids():
        return "SELECT id FROM ids"

    @staticmethod
    def remove_id(id):
        return "DELETE FROM ids WHERE id = {0}".format(id)

    @staticmethod
    def select_handle(id, handle):
        return "SELECT (0) FROM ids WHERE id = {0} AND handle = '{1}'".format(id, handle)

    @staticmethod
    def select_handles(id):
        return "SELECT handle FROM ids WHERE id = {0}".format(id)

    @staticmethod
    def insert_handle(id, handle):
        return "INSERT INTO ids VALUES ({0}, '{1}')".format(id, handle)    

    @staticmethod
    def remove_handle(id, handle):
        return "DELETE FROM ids WHERE id = {0} AND handle = '{1}'".format(id, handle)
    
    @staticmethod
    def select_cf_handles(id):
        return """
            SELECT
                handles.cf_handle
            FROM
                ids
            INNER JOIN handles ON ids.handle = handles.handle
            WHERE
                ids.id = {0}
            """.format(id)
    
    @staticmethod
    def select_all_handles(handle):
        return "SELECT 1 FROM ids WHERE handle = '{0}' LIMIT 1".format(handle)


class keys_handler:
    """
    id, open, secret
    """
    @staticmethod
    def create_table():
        return "CREATE TABLE IF NOT EXISTS keys ( id INTEGER, open TEXT, secret TEXT )"
    
    @staticmethod
    def select_all():
        return "SELECT * FROM keys"

    @staticmethod
    def insert_keys(id, open, secret):
        return "INSERT INTO keys VALUES ({0}, '{1}', '{2}')".format(id, open, secret)

    @staticmethod
    def select_keys(id):
        return "SELECT open, secret FROM keys WHERE id = {0}".format(id)
    
    @staticmethod
    def remove_keys(id):
        return "DELETE FROM keys WHERE id = {0}".format(id)
    
    @staticmethod
    def drop_table():
        return "DROP TABLE keys"
    

class queue_handler:
    """
    id, type
    """
    @staticmethod
    def create_table():
        return "CREATE TABLE IF NOT EXISTS queue ( id INTEGER, type INTEGER )"
    
    @staticmethod
    def select_type(id):
        return "SELECT type FROM queue WHERE id = {0}".format(id)
    
    @staticmethod
    def insert_id(id, type):
        return "INSERT INTO queue VALUES ({0}, {1})".format(id, type)
    
    @staticmethod
    def remove_id(id):
        return "DELETE FROM queue WHERE id = {0}".format(id)
    
    @staticmethod
    def select_all():
        return "SELECT * FROM queue"
    


class handles_handler:
    """
    handle, cf_handle
    """
    @staticmethod
    def create_table():
        return "CREATE TABLE IF NOT EXISTS handles ( handle TEXT, cf_handle TEXT )"
    
    @staticmethod
    def select_all():
        return "SELECT * FROM handles"
    
    @staticmethod
    def select_cf_handle(handle):
        return "SELECT cf_handle FROM handles WHERE handle = '{0}'".format(handle)
    
    @staticmethod
    def insert_handles(handle, cf_handle):
        return "INSERT INTO handles VALUES ('{0}', '{1}')".format(handle, cf_handle)
    
    @staticmethod
    def remove_handle(handle):
        return "DELETE FROM handles WHERE handle = '{0}'".format(handle)


class contests_handler:
    """
    id
    """
    @staticmethod
    def create_table():
        return "CREATE TABLE IF NOT EXISTS contests ( id INTEGER )"
    
    @staticmethod
    def select_id(id):
        return "SELECT (0) FROM contests WHERE id = {0}".format(id)
    
    @staticmethod
    def insert_id(id):
        return "INSERT INTO contests VALUES ({0})".format(id)

def create_connection(name):
    try:
        connection = psycopg2.connect(
            database = name,
            user = 'postgres',
            password =  password,
            host = '127.0.0.1',
            port = '5432'
        )
        return connection
    except Exception as e:
        logger.error('error {0} occurred while creating connection to database'.format(str(e)))

def execute_query(connection, query):
    try:
        connection.cursor().execute(query)
        connection.commit()
    except Exception as e:
        logger.error('error {0} occurred while processing query; query = {1}'.format(str(e), query))

def execute_read_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        logger.error('error {0} occurred while reading; query = {1}'.format(str(e), query))

if __name__ == '__main__':
    connection = create_connection(dbname)

    execute_query(connection, ids_handler.create_table())
    execute_query(connection, keys_handler.create_table())
    execute_query(connection, queue_handler.create_table())
    execute_query(connection, handles_handler.create_table())
    execute_query(connection, contests_handler.create_table())

    connection.close()