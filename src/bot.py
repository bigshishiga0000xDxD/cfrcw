import telebot
from env import token

from logs import logger
from data import ids_handler
import data
import cf

Bot = telebot.TeleBot(token)

def send_message(chatId, message, mode = None):
    try:
        Bot.send_message(chatId, message, parse_mode = mode)
        return True
    except Exception as e:
        e = str(e)
        if 'Forbidden: bot was kicked from the group chat' in e or 'Forbidden: bot was blocked by the user' in e:
            with data.create_connection('cfrcw') as connection:
                data.execute_query(connection, ids_handler.remove_id(chatId))
        else:
            logger.error('Unknown error: {0}'.format(e))
            return False

def send_everyone(contestId):
    connection = data.create_connection('cfrcw')

    resp = set(data.execute_read_query(connection, ids_handler.select_all_ids()))
    contestants, name = cf.get_contestants(contestId)
    
    for x in resp:
        id = x[0]
        if contestants == None:
            send_message(id, 'Произошла ошибка codeforces')
        else:
            handles = data.execute_read_query(connection, ids_handler.select_handles(id))
            message = '{0} был обновлен!\n\n'.format(name)
            message += '`'

            maxLenNickname = max(map(len, map(lambda x: x[0], handles)))

            for y in handles:
                handle = y[0]
                if contestants.get(handle) == None:
                    continue
                oldRating = contestants[handle][0]
                newRating = contestants[handle][1]
                delta = newRating - oldRating
                if delta < 0:
                    delta = '-' + str(delta)
                else:
                    delta = '+' + str(delta)
                
                message += handle
                message += ': '
                message += ' ' * (maxLenNickname - len(handle))
                message += '{0} -> {1} ({2})\n'.format(oldRating, newRating, delta)
            
            send_message(id, message + '`', mode = 'markdown')

    connection.close()