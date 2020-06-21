from telebot import types

from data import ids_handler
from data import handles_handler
from data import keys_handler
from data import queue_handler
from var import groupSize
from cf import check_users
from cf import get_ratings
import data

def _remove_handles(id, args, connection):
    args = list(map(lambda x : x.lower(), args))

    for arg in args:
        data.execute_query(connection, ids_handler.remove_handle(id, arg))
        if data.execute_read_query(connection, ids_handler.select_all_handles(arg)) == []:
            data.execute_query(connection, handles_handler.remove_handle(arg))
    
    return 'Все хэндлы успешно удалены'

def __add_handles(id, handles, handles_cf, connection):
    for i in range(len(handles)):
        handle = handles[i]
        cf_handle = handles_cf[i]

        if data.execute_read_query(connection, ids_handler.select_handle(id, handle)) == []:
            data.execute_query(connection, ids_handler.insert_handle(id, handle))
        
        if data.execute_read_query(connection, handles_handler.select_cf_handle(handle)) == []:
            data.execute_query(connection, handles_handler.insert_handles(handle, cf_handle))
    return 'Все хэндлы успешно добавлены'

def _add_handles(id, args, connection):
    args = list(map(lambda x : x.lower(), args))
    args = list(set(args))

    query = list()
    handles = list()

    for i in range(len(args)):
        query.append(args[i])
        if i % groupSize == groupSize - 1 or i == len(args) - 1:
            status, resp = check_users(query)
            if status == 0:
                return 'Пользователь с хэндлом {0} не найден'.format(resp)
            elif status == -1:
                return 'Произошла ошибка codeforces'
            else:
                handles += resp
            query = list()
    
    return __add_handles(id, args, handles, connection)

def _add_keys(id, args, connection):
    data.execute_query(connection, keys_handler.remove_keys(id)) 
    data.execute_query(connection, keys_handler.insert_keys(id, args[0], args[1]))
    return 'Ключи добавлены'

def _cancel(id, connection):
    data.execute_query(connection, queue_handler.remove_id(id))
    return 'Отменено'

def _clear(id, connection):
    handles = data.execute_read_query(connection, ids_handler.select_handles(id))
    handles = map(lambda x : x[0], handles)
    _remove_handles(id, handles, connection)
    data.execute_query(connection, keys_handler.remove_keys(id))
    data.execute_query(connection, queue_handler.remove_id(id))
    return 'Все данные успешно удалены'
    

def create_keyboard():
    button = types.InlineKeyboardButton('Отменить', callback_data = 'cancel')
    table = types.InlineKeyboardMarkup()
    table.add(button)
    return table

def _list(id, connection):
    handles = data.execute_read_query(connection, ids_handler.select_cf_handles(id))
    if handles == []:
        return 'Хэндлов нет'
    else:
        resp = 'Хэндлы:\n'
        handles.sort(key = lambda x : x[0].lower())

        cnt = 1
        cntLen = len(str(len(handles)))
        for handle in handles:
            resp += str(cnt)
            resp += '. ' + ' ' * (cntLen - len(str(cnt)))
            resp += handle[0]
            resp += '\n'
            cnt += 1

        return '`' + resp + '`'

def _get_ratings(id, connection):
    handles = data.execute_read_query(connection, ids_handler.select_cf_handles(id))
    if handles == []:
        return 'Хэндлов нет'
    else:
        query = list()
        ratings = dict()

        for i in range(len(handles)):
            query.append(handles[i])
            if i % groupSize == groupSize - 1 or i == len(handles) - 1:
                _ratings = get_ratings(query)
                if _ratings == None:
                    return 'Произошла ошибка codeforces'

                for key, val in _ratings.items():
                    ratings[key] = val
                
                query = list()

        ratings = {key: val for key, val in sorted(ratings.items(), key = lambda item: item[1], reverse = True)}
        res = ''

        maxLenNickname = max(map(len, map(lambda x: x[0], ratings.keys())))

        for item in ratings.items():
            res += item[0][0]
            res += ': '
            res += ' ' * (maxLenNickname - len(item[0][0]))
            res += str(item[1])
            res += '\n'
        return '`' + res + '`'