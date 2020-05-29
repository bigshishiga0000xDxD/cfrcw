from logs import logger
from bot import Bot
from bot import send_message
from data import ids_handler
from data import keys_handler
import data
import cf

@Bot.message_handler(commands = ['start'])
def start_message(message):
    send_message(message.chat.id, 'Напишите /help чтобы увидеть список команд')

@Bot.message_handler(commands = ['add'])
def add_id(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    if data.execute_read_query(connection, ids_handler.select_id(id)) == []:
        data.execute_query(connection, ids_handler.insert_id(id))
        send_message(id, 'Добавлено')
    else:
        send_message(id, 'Чат уже добавлен')
    
    connection.close()

@Bot.message_handler(commands = ['remove'])
def remove_id(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    if data.execute_read_query(connection, ids_handler.select_id(id)) != []:
        data.execute_query(connection, ids_handler.remove_id(id))
        send_message(id, 'Удалено')
    else:
        send_message(id, 'Чат уже удален/еще не добавлен')

    connection.close()

def __add_handles(id, args, connection):
    for handle in args:
        if data.execute_read_query(connection, ids_handler.select_handle(id, handle)) == []:
            data.execute_query(connection, ids_handler.insert_handle(id, handle))

def _add_handles(id, args, connection):
    args = list(map(lambda x : x.lower(), args))
    args = list(set(args))
    
    def exec_query(query):
        status, resp = cf.check_users(query)
        if status == 0:
            send_message(id, 'Пользователь с хэндлом {0} не найден'.format(resp))
            return None
        elif status == -1:
            send_message(id, 'Произошла ошибка codeforces')
            return None
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
    
    __add_handles(id, handles, connection)
    
    send_message(id, 'Все хэндлы успешно добавлены')

@Bot.message_handler(commands = ['addhandles'])
def add_handles(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    args = message.text.split()[1:]
    if len(args) == 0:
        send_message(id, 'Нет аргументов. Посмотрите /help')
    else:
        _add_handles(id, args, connection)

    connection.close()


@Bot.message_handler(commands = ['removehandles'])
def remove_handles(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    args = message.text.split()[1:]
    if len(args) == 0:
        send_message(id, 'Нет аргументов. Посмотрите /help')
    else:
        message = str()

        for arg in args:
            if data.execute_read_query(connection, ids_handler.select_handle(id, arg)) != []:
                data.execute_query(connection, ids_handler.remove_handle(id, arg))
                send_message(id, '{0} - Успех\n'.format(arg))
            else:
                send_message(id, '{0} - Хэндл еще не добавлен/уже удален\n'.format(arg))

    connection.close()

@Bot.message_handler(commands = ['listhandles'])
def list_handles(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    handles = data.execute_read_query(connection, ids_handler.select_handles(id))
    if handles == []:
        send_message(id, 'Хэндлов нет')
    else:
        resp = 'Хэндлы:\n'

        for handle in handles:
            resp += handle[0]
            resp += '\n'

        send_message(id, resp)

    connection.close()

@Bot.message_handler(commands = ['getratings'])
def get_ratings(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    handles = data.execute_read_query(connection, ids_handler.select_handles(id))
    if handles == []:
        send_message(id, 'Хэндлов нет')
    else:
        groupSize = 100
        query = list()
        ratings = dict()

        for i in range(len(handles)):
            if i % groupSize == groupSize - 1:
                _ratings = cf.get_ratings(query)
                if _ratings == None:
                    send_message(id, 'Произошла ошибка codeforces')
                    return                

                for key, val in _ratings.items():
                    ratings[key] = val
                
                query = list()
            query.append(handles[i])
        
        if len(query) != 0:
            for key, val in cf.get_ratings(query).items():
                ratings[key] = val

        ratings = {key: val for key, val in sorted(ratings.items(), key = lambda item: item[1], reverse = True)}
        res = ''

        for item in ratings.items():
            res += item[0][0]
            res += ': '
            res += str(item[1])
            res += '\n'
        
        send_message(id, res)
    
    connection.close()

@Bot.message_handler(commands = ['sync'])
def sync(message):
    id = message.chat.id
    if (message.chat.type == 'group'):
        send_message(id, 'Эта команда не может быть выполнена в групповых чатах в целях безопасности ваших данных')
    else:
        connection = data.create_connection('list.db')

        elems = data.execute_read_query(connection, keys_handler.select_keys(id))
        if elems == []:
            send_message(id, 'Вы не добавили api ключи. Посмотрите /help')
        else:
            open, secret = elems[0]
            handles, status = cf.get_friends(open, secret)
            
            if handles == None:
                if 'Incorrect API key' in status:
                    send_message(id, 'Вы указали неправильные ключи')
                else:
                    send_message(id, 'Что-то пошло не так. Скорее всего, codeforces сейчас недоступен.')
                    logger.critical(status)
            else:
                __add_handles(id, handles, connection)
                send_message(id, 'Успех')
        
        connection.close()
        
        

@Bot.message_handler(commands = ['addkeys'])
def add_keys(message):
    id = message.chat.id
    if (message.chat.type == 'group'):
        send_message(id, 'Эта команда не может быть выполнена в групповых чатах в целях безопасности ваших данных')
    else:
        connection = data.create_connection('list.db')
        args = message.text.split()[1:]

        if len(args) != 2:
            send_message(id, 'Неверные аргументы. Посмотрите /help')
        else:
            if data.execute_read_query(connection, keys_handler.select_keys(id)) != []:
                data.execute_query(connection, keys_handler.remove_keys(id))
            
            data.execute_query(connection, keys_handler.insert_keys(id, args[0], args[1]))
            send_message(id, 'Успех')
        connection.close()

@Bot.message_handler(commands = ['help'])
def help(message):
    send_message(message.chat.id, """
    Комманды:\n
/help - Вывести это сообщение\n
/add - Разрешить сообщения об обновлении рейтинга в этом чате\n
/remove - Запретить сообщения об обновлении рейтинга в этом чате. Удаляя чат этой командой, вы также удаляете все связанные с ним хэндлы\n
/addhandles [handle1, handle2, ...] - Дополнительно будет присылаться изменение рейтинга пользователей c указанными хэндлами (если они писали контест). Обратите внимание, что если пользователь изменит хэндл, вам нужно будет добавить его снова под новым хэндлом\n
/removehandles [handle1, handle2, ...] - Изменение рейтинга указанных пользователей присылаться не будет\n
/listahandles - Вывести список всех добавленных в этот чат хэндлов\n
/getratings - Вывести список добавленных хэндлов, отсортированных по рейтингу\n
/sync - Сихронизировать список ваших друзей с текущим списком. Чтобы выполнить эту команду необходимо сначала выполнить /addkeys. /sync не удаляет ваш текущий список хэндлов. Если вам необходимо полностью синхронизировать списки, выполните сначала /remove\n
/addkeys - Добавить api ключи. Вы можете создать их здесь https://codeforces.com/settings/api. Для этого нажмите кнопку "Добавить ключ API" и в качестве названия напишите, например, `cfrcw`, а в поле пароль - свой пароль от аккаунта codeforces. В аргументах команды необходимо сначала ввести ключ `key`, а затем ключ `secret`. Поскольку второй ключ является секретным, эта команда отключена в групповых чатах.
\nПо поводу любых вопросов и предложений писать сюда @sheshenya
    """, mode = 'markdown')