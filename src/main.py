from time import sleep
from threading import Thread

import cf
import commands
from logs import logger
from bot import Bot
from bot import send_everyone

def watch_changes(interval = 60):
    contests = dict()
    while True:
        cf.update_contests(contests = contests)
        sleep(interval)
        res = cf.check_changes(contests)
        
        for t in res:
            send_everyone(t)

# main

try:
    thread1 = Thread(target = Bot.polling)
    thread2 = Thread(target = watch_changes)
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
