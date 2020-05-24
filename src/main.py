from time import sleep
from threading import Thread

import util
import data
import commands
from logs import logger
from bot import bot

def send_message(chatId, message):
    try:
        bot.send_message(chatId, message)
    except Exception as e:
        e = str(e)
        if 'Forbidden: bot was kicked from the group chat' in e or 'Forbidden: bot was blocked by the user' in e:
            data.execute_query(connection, data.remove_id(x[0]))
        else:
            logger.error('Unknown error: {0}'.format(e))

def send_everyone(s):
    connection = data.create_connection('list.db')

    resp = set(data.execute_read_query(connection, data.select_all_ids()))
    contestants, name = util.get_contestants(s)
    
    for x in resp:
        if contestants == None:
            send_message('Произошла ошибка codeforces')
        else:
            id = x[0]
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

def watch_changes(interval):
    while True:
        contests = util.update_contests()
        sleep(interval)
        res = util.check_changes(contests)
        
        for t in res:
            send_everyone(t)
        
        

# main

try:
    thread1 = Thread(target = bot.polling)
    thread2 = Thread(target = watch_changes, args = (30,))
    thread1.daemon = True
    thread2.daemon = True
    thread1.start()
    thread2.start()
    logger.debug('started')
    while True: sleep(100)
except (KeyboardInterrupt, SystemExit):
    print('\b \b\b \binterrupted')
    logger.debug('interrupted')
except Exception as e:
    logger.critical(str(e))
