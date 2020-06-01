from logs import logger
from bot import Bot
from bot import send_message
from env import path
from data import ids_handler
from data import keys_handler
from data import queue_handler
import util
import data
import cf


@Bot.message_handler(commands = ['start'])
def start_message(message):
    id = message.chat.id
    send_message(id, 'Напишите /help чтобы увидеть список команд')

@Bot.message_handler(commands = ['clear'])
def remove_id(message):
    id = message.chat.id
    connection = data.create_connection(path + 'list.db')

    data.execute_query(connection, ids_handler.remove_id(id))
    send_message(id, 'Удалено')

    connection.close()

@Bot.message_handler(commands = ['add'])
def add_handles(message):
    id = message.chat.id
    connection = data.create_connection(path + 'list.db')

    args = message.text.split()[1:]
    if len(args) == 0:
        data.execute_query(connection, queue_handler.remove_id(id))
        data.execute_query(connection, queue_handler.insert_id(id, 0))
        send_message(id, 'Введите хэндлы или напишите /cancel для отмены')
    else:
        util._add_handles(id, args, connection)

    connection.close()


@Bot.message_handler(commands = ['remove'])
def remove_handles(message):
    id = message.chat.id
    connection = data.create_connection(path + 'list.db')

    args = message.text.split()[1:]
    if len(args) == 0:
        data.execute_query(connection, queue_handler.remove_id(id))
        data.execute_query(connection, queue_handler.insert_id(id, 1))
        send_message(id, 'Введите хэндлы или напишите /cancel для отмены')
    else:
        util._remove_handles(id, args, connection)

    connection.close()

@Bot.message_handler(commands = ['list'])
def list_handles(message):
    id = message.chat.id
    connection = data.create_connection(path + 'list.db')

    handles = data.execute_read_query(connection, ids_handler.select_cf_handles(id))
    if handles == []:
        send_message(id, 'Хэндлов нет')
    else:
        resp = 'Хэндлы:\n'

        for handle in handles:
            resp += handle[0]
            resp += '\n'

        send_message(id, resp)

    connection.close()

@Bot.message_handler(commands = ['ratings'])
def get_ratings(message):
    id = message.chat.id
    connection = data.create_connection(path + 'list.db')

    handles = data.execute_read_query(connection, ids_handler.select_cf_handles(id))
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

        maxLenNickname = max(map(len, map(lambda x: x[0], ratings.keys())))

        for item in ratings.items():
            res += item[0][0]
            res += ': '
            res += ' ' * (maxLenNickname - len(item[0][0]))
            res += str(item[1])
            res += '\n'
        send_message(id, "`" + res + "`", mode = 'markdown')
    
    connection.close()

@Bot.message_handler(commands = ['sync'])
def sync(message):
    id = message.chat.id
    if (message.chat.type == 'group'):
        send_message(id, 'Эта команда не может быть выполнена в групповых чатах в целях безопасности ваших данных')
    else:
        connection = data.create_connection(path + 'list.db')

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
                util.__add_handles(id, list(map(lambda x : x.lower(), handles)), handles, connection)
                send_message(id, 'Успех')
        
        connection.close()
        
        

@Bot.message_handler(commands = ['addkeys'])
def add_keys(message):
    id = message.chat.id
    if (message.chat.type == 'group'):
        send_message(id, 'Эта команда не может быть выполнена в групповых чатах в целях безопасности ваших данных')
    else:
        connection = data.create_connection(path + 'list.db')
        args = message.text.split()[1:]

        if len(args) == 2:
            util._add_keys(id, args, connection)
        elif len(args) == 0:
            send_message(id, 'Введите ключи или напишите /cancel для отмены')
            data.execute_query(connection, queue_handler.insert_id(id, 2))
        else:
            send_message(id, 'Неверные аргументы. Посмотрите /help')
        
        connection.close()


@Bot.message_handler(commands = ['cancel'])
def cancel(message):
    id = message.chat.id
    connection = data.create_connection(path + 'list.db')

    resp = data.execute_read_query(connection, queue_handler.select_type(id))
    if resp == []:
        send_message(id, 'Нечего отменять')
    else:
        data.execute_query(connection, queue_handler.remove_id(id))
        send_message(id, 'Отменено')
    
    connection.close()


@Bot.message_handler(commands = ['help'])
def help(message):
    send_message(message.chat.id, """
    Комманды:\n
/help - Вывести это сообщение.\n
/add `handle1` `handle2` ... - Будут присылаться изменения рейтинга пользователей c указанными хэндлами (если они писали контест). Обратите внимание, что если пользователь изменит хэндл, вам нужно будет добавить его снова под новым хэндлом. Можно запустить без параметров и ввести хэндлы следующим сообщением.\n
/remove `handle1` `handle2` ... - Изменения рейтинга указанных пользователей присылаться не будет. Можно запустить без параметров и ввести хэндлы следующим сообщением.\n
/clear - Удалить все хэндлы и запретить сообщения.\n
/list - Вывести список всех добавленных в этот чат хэндлов.\n
/ratings - Вывести список добавленных хэндлов, отсортированных по рейтингу.\n
/sync - Сихронизировать список ваших друзей с текущим списком. Чтобы выполнить эту команду необходимо сначала выполнить /addkeys. /sync не удаляет ваш текущий список хэндлов. Если вам необходимо полностью синхронизировать списки, выполните сначала /clear.\n
/addkeys `key` `secret` - Добавить api ключи. Вы можете создать их здесь https://codeforces.com/settings/api. Для этого нажмите кнопку "Добавить ключ API" и в качестве названия напишите, например, `cfrcw`, а в поле пароль - свой пароль от аккаунта codeforces. Поскольку второй ключ является секретным, эта команда отключена в групповых чатах. Можно запустить без параметров и ввести хэндлы следующим сообщением.\n
\nПо поводу любых вопросов и предложений писать сюда @sheshenya
    """, mode = 'markdown')

@Bot.message_handler(content_types = ['text'])
def text_handler(message):
    id = message.chat.id
    connection = data.create_connection(path + 'list.db')
    
    resp = data.execute_read_query(connection, queue_handler.select_type(id))
    if resp == []:
        return

    data.execute_query(connection, queue_handler.remove_id(id))
    args = message.text.split()
    if resp[0][0] == 0:
        util._add_handles(id, args, connection)
    elif resp[0][0] == 1:
        util._remove_handles(id, args, connection)
    else:
        util._add_keys(id, args, connection)
    
    
    connection.close()