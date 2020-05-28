from bot import Bot
from bot import send_message
from data import ids_handler
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

@Bot.message_handler(commands = ['addhandles'])
def add_handles(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    args = message.text.split()[1:]
    if len(args) == 0:
        send_message(id, 'Нет аргументов. Посмотрите /help')
    else:
        for arg in args:
            status = cf.check_user(arg)
            isEmpty = data.execute_read_query(connection, ids_handler.select_handle(id, arg)) == []

            if isEmpty and status == 1:
                data.execute_query(connection, ids_handler.insert_handle(id, arg))
                send_message(id, '{0} - Успех\n'.format(arg))
            elif not isEmpty:
                send_message(id, '{0} - Хэндл уже добавлен\n'.format(arg))
            elif status == 0:
                send_message(id, '{0} - Указанного хэндла не существует\n'.format(arg))
            elif status == -1:
                send_message(id, 'Произошла ошибка codeforces. Попробуйте позже')
                break

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
                print(query)
                for key, val in cf.get_ratings(query).items():
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
        

@Bot.message_handler(commands = ['help'])
def help(message):
    send_message(message.chat.id, """
    Комманды:\n
/help - Вывести это сообщение\n
/add - Разрешить сообщения об обновлении рейтинга в этом чате\n
/remove - Запретить сообщения об обновлении рейтинга в этом чате. Удаляя чат этой командой, вы также удаляете все связанные с ним хэндлы\n
/addhandle [handle1, handle2, ...] - Дополнительно будет присылаться изменение рейтинга пользователей c указанными хэндлами (если они писали контест). Обратите внимание, что если пользователь изменит хэндл, вам нужно будет добавить его снова под новым хэндлом\n
/removehandle [handle1, handle2, ...] - Изменение рейтинга указанных пользователей присылаться не будет\n
/listahandles - Вывести список всех добавленных в этот чат хэндлов\n
/getratings - Вывести список добавленных хэндлов, отсортированных по рейтингу\n
\nПо поводу любых вопросов и предложений писать сюда @sheshenya
    """)