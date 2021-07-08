import telebot
from time import sleep

from var import token
from var import dbname
from logs import logger
from data import ids_handler
from util import _clear
from util import split_string
import data
import cf

Bot = telebot.TeleBot(token)

def send_message(chatId, message, mode = None, markup = None, \
                 web_page_preview = True, all_monospace = False, header = None):
    try:
        if all_monospace:
            mode = 'markdown'

        splitted_text = split_string(message, 3000)

        for text in splitted_text:
            if all_monospace:
                text = '`' + text + '`'
            if header is not None:
                text = header + text
                header = None

            success = False
            while not success:
                try:
                    Bot.send_message(
                        chatId,
                        text,
                        parse_mode = mode,
                        reply_markup = markup,
                        disable_web_page_preview = not web_page_preview
                    )
                    success = True
                except Exception as e:
                    se = str(e)
                    if 'Too Many Requests' in se:
                        time = int(se[se.find('retry_after') + len('retry_after') + 1:-4]) + 0.5
                        sleep(time)
                    else:
                        raise e
        return True
    except Exception as e:
        e = str(e)
        if 'Forbidden: bot was kicked from the group chat' in e or \
                'Forbidden: bot was blocked by the user' in e:
            with data.create_connection(dbname) as connection:
                _clear(chatId, connection)
        else:
            logger.error('Unknown error: {0}'.format(e))
            return False

def edit_message(chatId, messageId, message):
    try:
        Bot.edit_message_text(message, chatId, message_id = messageId)
        return True
    except Exception as e:
        e = str(e)
        if 'Forbidden: bot was kicked from the group chat' in e or \
                'Forbidden: bot was blocked by the user' in e:
            with data.create_connection(dbname) as connection:
                _clear(chatId, connection)
        elif not 'Bad Request: message is not modified' in e:
            logger.error('Unknown error: {0}'.format(e))
            return False

def send_everyone(contestId):
    connection = data.create_connection(dbname)

    ids = data.execute_read_query(connection, ids_handler.select_all_ids())
    contestants, name = cf.get_contestants(contestId)
    if contestants is None:
        connection.close()
        return

    for x in ids:
        id = x[0]
        handles = data.execute_read_query(connection, ids_handler.select_cf_handles(id))

        maxLenNickname = 0
        for y in handles:
            handle = y[0]
            if contestants.get(handle) is None:
                continue
            maxLenNickname = max(maxLenNickname, len(handle))

        if maxLenNickname == 0:
            continue

        results = list()

        for y in handles:
            handle = y[0]
            if contestants.get(handle) is None:
                continue
            oldRating = contestants[handle][0]
            newRating = contestants[handle][1]
            delta = newRating - oldRating
            if delta < 0:
                delta = str(delta)
            else:
                delta = '+' + str(delta)

            results.append((handle, oldRating, newRating, delta))

        results.sort(reverse = True, key = lambda x : int(x[3]))

        header = '[{0}](https://codeforces.com/contest/{1}) был обновлен!\n\n'.format(name, contestId)
        message = ''

        for handle, oldRating, newRating, delta in results:
            message += handle
            message += ': '
            message += ' ' * (maxLenNickname - len(handle))
            message += '{0} -> {1} ({2})\n'.format(oldRating, newRating, delta)

        send_message(
            id,
            message,
            header = header,
            mode = 'markdown',
            web_page_preview = False,
            all_monospace = True
        )

    connection.close()
