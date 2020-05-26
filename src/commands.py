from bot import Bot
from bot import send_message
import data
import util

@Bot.message_handler(commands = ['start'])
def start_message(message):
    send_message(message.chat.id, 'Напишите /help чтобы увидеть список команд')

@Bot.message_handler(commands = ['add'])
def add_id(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    if data.execute_read_query(connection, data.select_id(id)) == []:
        data.execute_query(connection, data.insert_id(id))
        send_message(id, 'Добавлено')
    else:
        send_message(id, 'Чат уже добавлен')
    
    connection.close()

@Bot.message_handler(commands = ['remove'])
def remove_id(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    if data.execute_read_query(connection, data.select_id(id)) != []:
        data.execute_query(connection, data.remove_id(id))
        send_message(id, 'Удалено')
    else:
        send_message(id, 'Чат уже удален/еще не добавлен')

    connection.close()

@Bot.message_handler(commands = ['addhandle'])
def add_handle(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    text = message.text.split()
    if len(text) != 2:
        send_message(id, 'Неправильные аргументы. Посмотрите /help')
    else:
        arg = text[1]
        status = util.check_user(arg)

        if status == 1:
            if data.execute_read_query(connection, data.select_handle(id, arg)) == []:
                data.execute_query(connection, data.insert_handle(id, arg))
                send_message(id, 'Успех')
            else:
                send_message(id, 'Хэндл уже добавлен')
        elif status == 0:
            send_message(id, 'Указанного хэндла не существует')
        elif status == -1:
            send_message(id, 'Произошла ошибка codeforces')

    connection.close()


@Bot.message_handler(commands = ['removehandle'])
def remove_handle(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    text = message.text.split()
    if len(text) != 2:
        send_message(id, 'Неправильные аргументы. Посмотрите /help')
    else:
        arg = text[1]

        if data.execute_read_query(connection, data.select_handle(id, arg)) != []:
            data.execute_query(connection, data.remove_handle(id, arg))
            send_message(id, 'Успех')
        else:
            send_message(id, 'Хэндл еще не добавлен/уже удален')
    
    connection.close()

@Bot.message_handler(commands = ['listhandles'])
def list_handles(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    handles = data.execute_read_query(connection, data.select_handles(id))
    resp = 'Хэндлы:\n'

    for handle in handles:
        resp += handle[0]
        resp += '\n'

    send_message(id, resp)

    connection.close()

@Bot.message_handler(commands = ['help'])
def help(message):
    send_message(message.chat.id, """
    Комманды:\n
/help - Вывести это сообщение\n
/add - Разрешить сообщения об обновлении рейтинга в этом чате\n
/remove - Запретить сообщения об обновлении рейтинга в этом чате. Удаляя чат этой командой, вы также удаляете все связанные с ним хэндлы\n
/addhandle [handle] - Дополнительно будет присылаться изменение рейтинга пользователя c хэндлом handle (если он писал контест). Обратите внимание, что если пользователь изменит хэндл, вам нужно будет добавить его снова\n
/removehandle [handle] - Изменение рейтинга пользователя handle присылаться не будет\n
/listahandles - Вывести список всех добавленных в этот чат хэндлов
\nПо поводу любых вопросов и предложений писать сюда @sheshenya
    """)