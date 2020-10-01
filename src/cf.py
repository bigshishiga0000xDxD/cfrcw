import requests
import json

from logs import logger
from auth import make_query
from var import dbname, maxTime
from data import contests_handler
import data

def check_changes():
    try:
        resp = requests.get('https://codeforces.com/api/contest.list?gym=false').json()
    except Exception as e:
        logger.critical(str(e))
        return list()

    if resp['status'] == 'FAILED':
        logger.critical(resp['comment'])
        return list()

    res = list()
    connection = data.create_connection(dbname)

    i = 0
    while resp['result'][i]['relativeTimeSeconds'] < maxTime:
        id = resp['result'][i]['id']

        if resp['result'][i]['phase'] != 'FINISHED' or \
                data.execute_read_query(connection, contests_handler.select_id(id)) != []:
            i += 1
            continue

        try:
            resp2 = requests.get('https://codeforces.com/api/contest.ratingChanges?contestId={0}'.format(id)).json()
        except Exception as e:
            logger.critical(str(e))
            i += 1
            continue

        logger.debug('i = {0}; id = {1};'.format(i, id))

        if resp2['status'] == 'OK' and resp2['result'] != []:
            res.append(id)
            data.execute_query(connection, contests_handler.insert_id(id))
        i += 1


    connection.close()
    logger.debug('found {0}'.format(res))

    return res


def check_users(handles):
    url = 'https://codeforces.com/api/user.info?handles='
    for handle in handles:
        url += handle
        url += ';'

    try:
        resp = requests.get(url).json()
    except Exception as e:
        logger.critical(str(e))
        return (-1, None)

    if resp['status'] == 'OK':
        handles = list()
        for x in resp['result']:
            handles.append(x['handle'])
        return (1, handles)
    elif resp['comment'].startswith('handles: User with handle') and resp['comment'].endswith('not found'):
        s = resp['comment']
        return (0, s[s.find('handle ') + 7 : s.find('not') - 1])
    else:
        logger.critical(resp['comment'])
        return (-1, None)

def get_contestants(id):
    try:
        resp = requests.get('https://codeforces.com/api/contest.ratingChanges?contestId={0}'.format(id)).json()
    except Exception as e:
        logger.critical(str(e))
        return (None, None)

    if resp['status'] == 'FAILED':
        logger.critical(resp['comment'])
        return (None, None)
    else:
        res = dict()
        for i in range(len(resp['result'])):
            res[resp['result'][i]['handle']] = \
                (resp['result'][i]['oldRating'], resp['result'][i]['newRating'])
        return (res, resp['result'][0]['contestName'])

def get_ratings(handles):
    query = ''
    for handle in handles:
        query += handle[0]
        query += ';'

    try:
        resp = requests.get('https://codeforces.com/api/user.info?handles={0}'.format(query)).json()
    except Exception as e:
        logger.critical(str(e))
        return None

    if resp['status'] == 'FAILED':
        logger.critical(resp['comment'])
        return None
    else:
        res = dict()
        for i in range(len(handles)):
            res[handles[i]] = resp['result'][i]['rating']
        return res

def get_friends(open, secret):
    url = make_query({'onlyOnline': 'false'}, 'user.friends', open, secret)

    try:
        resp = requests.get(url).json()
    except Exception:
        return (None, 'connection error')

    if resp['status'] == 'FAILED':
        return (None, resp['comment'])
    else:
        result = list()
        for handle in resp['result']:
            result.append(handle)
        return (result, None)
