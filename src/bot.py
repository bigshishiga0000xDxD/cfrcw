import telebot
from configparser import ConfigParser

from logs import logger
import util

config = ConfigParser()
config.read('settings.ini')

Bot = telebot.TeleBot(config.get('config', 'Token'))

def send_message(chatId, message):
    try:
        Bot.send_message(chatId, message)
    except Exception as e:
        e = str(e)
        if 'Forbidden: bot was kicked from the group chat' in e or 'Forbidden: bot was blocked by the user' in e:
            data.execute_query(connection, data.remove_id(chatId))
        else:
            logger.error('Unknown error: {0}'.format(e))

def send_everyone(contestId):
    connection = data.create_connection('list.db')

    resp = set(data.execute_read_query(connection, data.select_all_ids()))
    contestants, name = util.get_contestants(contestId)
    
    for x in resp:
        id = x[0]
        if contestants == None:
            send_message(id, 'Произошла ошибка codeforces')
        else:
            handles = data.execute_read_query(connection, data.select_handles(id))
            message = '{0} был обновлен!\n'.format(name)

            for y in handles:
                handle = y[0]
                if handle == None or contestants.get(handle) == None:
                    continue
                oldRating = contestants[handle][0]
                newRating = contestants[handle][1]
                delta = newRating - oldRating
                if delta < 0:
                    delta = '-' + str(delta)
                else:
                    delta = '+' + str(delta)
                
                message += '{0}: {1} -> {2} ({3})\n'.format(handle, oldRating, newRating, delta)
            
            send_message(id, message)

    connection.close()