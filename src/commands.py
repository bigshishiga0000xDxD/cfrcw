from logs import logger
from bot import Bot
from bot import send_message
from bot import edit_message
from env import dbname
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
    with data.create_connection(dbname) as connection:
        send_message(id, util._clear(id, connection))

@Bot.message_handler(commands = ['add'])
def add_handles(message):
    id = message.chat.id
    connection = data.create_connection(dbname)

    args = message.text.split()[1:]
    if len(args) == 0:
        data.execute_query(connection, queue_handler.remove_id(id))
        data.execute_query(connection, queue_handler.insert_id(id, 0))
        send_message(id, 'Введите хэндлы', markup = util.create_keyboard())
    else:
        send_message(id, util._add_handles(id, args, connection))

    connection.close()


@Bot.message_handler(commands = ['remove'])
def remove_handles(message):
    id = message.chat.id
    connection = data.create_connection(dbname)

    args = message.text.split()[1:]
    if len(args) == 0:
        data.execute_query(connection, queue_handler.remove_id(id))
        data.execute_query(connection, queue_handler.insert_id(id, 1))
        send_message(id, 'Введите хэндлы', markup = util.create_keyboard())
    else:
        send_message(id, util._remove_handles(id, args, connection))

    connection.close()

@Bot.message_handler(commands = ['list'])
def list_handles(message):
    id = message.chat.id
    with data.create_connection(dbname) as connection:
        send_message(id, util._list(id, connection))
    connection.close()

@Bot.message_handler(commands = ['ratings'])
def get_ratings(message):
    id = message.chat.id
    with data.create_connection(dbname) as connection:
        send_message(id, util._get_ratings(id, connection), mode = 'markdown')

@Bot.message_handler(commands = ['sync'])
def sync(message):
    id = message.chat.id
    if (message.chat.type == 'group'):
        send_message(id, 'Эта команда не может быть выполнена в групповых чатах в целях безопасности ваших данных')
    else:
        connection = data.create_connection(dbname)

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
                send_message(id, util.__add_handles(id, list(map(lambda x : x.lower(), handles)), handles, connection))
        
        connection.close()
        
        

@Bot.message_handler(commands = ['addkeys'])
def add_keys(message):
    id = message.chat.id
    if (message.chat.type == 'group'):
        send_message(id, 'Эта команда не может быть выполнена в групповых чатах в целях безопасности ваших данных')
    else:
        connection = data.create_connection(dbname)
        args = message.text.split()[1:]

        if len(args) == 2:
            send_message(id, util._add_keys(id, args, connection))
        elif len(args) == 0:
            send_message(id, 'Введите ключи', markup = util.create_keyboard())
            data.execute_query(connection, queue_handler.insert_id(id, 2))
        else:
            send_message(id, 'Неверные аргументы. Посмотрите /help')
        
        connection.close()


@Bot.message_handler(commands = ['help'])
def help(message):
    send_message(message.chat.id, """
    Комманды:\n
/help - Вывести это сообщение.\n
/add `handle1` `handle2` `...` - Будут присылаться изменения рейтинга пользователей c указанными хэндлами (если они писали контест). Обратите внимание, что если пользователь изменит хэндл, вам нужно будет добавить его снова под новым хэндлом. Можно запустить без параметров и ввести хэндлы следующим сообщением.\n
/remove `handle1` `handle2` `...` - Изменения рейтинга указанных пользователей присылаться не будет. Можно запустить без параметров и ввести хэндлы следующим сообщением.\n
/clear - Удалить все хэндлы и запретить сообщения.\n
/list - Вывести список всех добавленных в этот чат хэндлов.\n
/ratings - Вывести список добавленных хэндлов, отсортированных по рейтингу.\n
/sync - Сихронизировать список ваших друзей с текущим списком. Чтобы выполнить эту команду необходимо сначала выполнить /addkeys. /sync не удаляет ваш текущий список хэндлов. Если вам необходимо полностью синхронизировать списки, выполните сначала /clear.\n
/addkeys `key` `secret` - Добавить api ключи. Вы можете создать их здесь https://codeforces.com/settings/api. Для этого нажмите кнопку "Добавить ключ API" и в качестве названия напишите, например, `cfrcw`, а в поле пароль - свой пароль от аккаунта codeforces. Поскольку второй ключ является секретным, эта команда отключена в групповых чатах. Можно запустить без параметров и ввести хэндлы следующим сообщением.\n
\nПо поводу любых вопросов и предложений писать сюда @sheshenya
    """, mode = 'markdown')

@Bot.callback_query_handler(func = lambda call: True)
def cancel_button_handler(call):
    chatId = call.message.chat.id
    messageId = call.message.message_id
    try:
        if call.message and call.data == 'cancel':
            with data.create_connection(dbname) as connection:
                edit_message(chatId, messageId, util._cancel(chatId, connection))    
            
    except Exception as e:
        logger.error(str(e))

@Bot.message_handler(content_types = ['text'])
def text_handler(message):
    id = message.chat.id
    connection = data.create_connection(dbname)
    
    resp = data.execute_read_query(connection, queue_handler.select_type(id))
    if resp == []:
        return

    data.execute_query(connection, queue_handler.remove_id(id))
    args = message.text.split()
    if resp[0][0] == 0:
        message = util._add_handles(id, args, connection)
    elif resp[0][0] == 1:
        message = util._remove_handles(id, args, connection)
    else:
        message = util._add_keys(id, args, connection)
    send_message(id, message)
    
    connection.close()