#!/usr/bin/python3

from time import sleep
from threading import Thread

from logs import logger
from bot import Bot
from bot import send_everyone
from var import interval
import cf
import commands

def watch_changes():
    while True:
        contests = cf.check_changes()
        for id in contests:
            send_everyone(id)
        sleep(interval)

# main

try:
    thread1 = Thread(target = Bot.infinity_polling)
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
