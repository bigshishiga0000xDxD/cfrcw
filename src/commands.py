from bot import bot
import data

@bot.message_handler(commands = ['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Напишите /help чтобы увидеть список команд')

@bot.message_handler(commands = ['add'])
def add_id(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    if data.execute_read_query(connection, data.select_id(id)) == []:
        data.execute_query(connection, data.insert_id(id, 3))
    bot.send_message(id, 'Добавлено')
    
    connection.close()

@bot.message_handler(commands = ['remove'])
def delete_id(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    if data.execute_read_query(connection, data.select_id(id)) != []:
        data.execute_query(connection, data.remove_id(id))
    bot.send_message(id, 'Удалено')

    connection.close()

@bot.message_handler(commands = ['setlevel'])
def set_level(message):
    id = message.chat.id
    connection = data.create_connection('list.db')

    if data.execute_read_query(connection, data.select_id(id)) != []:
        text = message.text.split()
        if len(text) != 2 or not text[1].isdigit() or len(text[1]) > 1 or int(text[1]) < 1 or int(text[1]) > 3:
            bot.send_message(id, 'Неправильные аргументы. Посмотрите /help')
        else:
            arg = int(text[1])
            data.execute_query(connection, data.update_level(id, arg))
            bot.send_message(id, 'Успех')
    else:
        bot.send_message(id, 'Необходимо сначала добавить чат. Посмотрите /help')

    connection.close()

@bot.message_handler(commands = ['help'])
def help(message):
    bot.send_message(message.chat.id, """
        Комманды:\n
        /help - Вывести это сообщение\n
        /add - Разрешить сообщения об обновлении рейтинга в этом чате\n
        /remove - Запретить сообщения об обновлении рейтинга в этом чате\n
        /setlevel - Указать, об изменениях в каких дивизионах следует сообщать. Возможные аргументы - 1, 2, или 3
        Например, /setlevel 2 - будет сообщаться об изменениях во втором и первом дивизионе,
        а также в div1 + div2 и Educational раундах, но не в третьем.\n\n
        По поводу любых вопросов и предложений писать сюда @sheshenya
    """)