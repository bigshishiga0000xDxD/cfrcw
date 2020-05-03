from time import sleep
from threading import Thread

import util
import data
import commands
from logs import logger
from bot import bot

def detect_div(s):
    if 'Div. 3' in s:
        return 3
    elif 'Educational' in s or 'Div. 2' in s:
        return 2
    else:
        return 1

def send_everyone(s):
    connection = data.create_connection('list.db')

    resp = data.execute_read_query(connection, data.select_all())
    div = detect_div(s)
    for x in resp:
        if div <= x[1]:
            try:
                bot.send_message(x[0], s)
            except Exception as e:
                if 'Forbidden: bot was kicked from the group chat' in str(e):
                    data.execute_query(connection, data.remove_id(x[0]))
                else:
                    logger.error('Unknown error: {0}'.format(str(e)))


    connection.close()

def watch_changes(interval):
    while True:
        contests = util.update_contests()
        sleep(interval)
        res = util.check_changes(contests)
        
        if len(res) > 0:
            for t in res:
                send_everyone(t + 'был обновлен!')
        
        

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
    print('\ninterrupted')
    logger.debug('interrupted')
