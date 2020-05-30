from bot import send_message
from data import ids_handler
from data import handles_handler
from data import keys_handler
from data import queue_handler
from cf import check_users
import data

def _remove_handles(id, args, connection):
    args = list(map(lambda x : x.lower(), args))

    for arg in args:
        data.execute_query(connection, ids_handler.remove_handle(id, arg))
    
    send_message(id, 'Все хэндлы успешно удалены')

def __add_handles(id, handles, handles_cf, connection):
    for i in range(len(handles)):
        handle = handles[i]
        cf_handle = handles_cf[i]

        if data.execute_read_query(connection, ids_handler.select_handle(id, handle)) == []:
            data.execute_query(connection, ids_handler.insert_handle(id, handle))
        
        if data.execute_read_query(connection, handles_handler.select_cf_handle(handle)) == []:
            data.execute_query(connection, handles_handler.insert_handles(handle, cf_handle))

def _add_handles(id, args, connection):
    args = list(map(lambda x : x.lower(), args))
    args = list(set(args))
    
    def exec_query(query):
        status, resp = check_users(query)
        if status == 0:
            send_message(id, 'Пользователь с хэндлом {0} не найден'.format(resp))
        elif status == -1:
            send_message(id, 'Произошла ошибка codeforces')
        else:
            return resp

    groupSize = 100
    query = list()
    handles = list()

    for i in range(len(args)):
        query.append(args[i])
        if i % groupSize == groupSize - 1:
            res = exec_query(query)
            if res == None:
                return
            else:
                handles += res
            query = list()
    
    res = exec_query(query)
    if res == None:
        return
    else:
        handles += res
    
    __add_handles(id, args, handles, connection)
    
    send_message(id, 'Все хэндлы успешно добавлены')

def _add_keys(id, args, connection):
    data.execute_query(connection, keys_handler.remove_keys(id)) 
    data.execute_query(connection, keys_handler.insert_keys(id, args[0], args[1]))
    send_message(id, 'Успех')
