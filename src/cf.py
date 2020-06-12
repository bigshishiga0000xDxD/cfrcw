import requests
import json

from logs import logger
from auth import make_query
from var import toCheck
from var import dbname
from data import contests_handler
import data

def update_contests(contests):
    try:
        resp = requests.get('https://codeforces.com/api/contest.list?gym=false').json()
    except Exception as e:
        logger.critical(str(e))
        return dict()

    if resp['status'] == 'FAILED':
        logger.critical(resp['comment'])
        return dict()

    skipped = list()
    connection = data.create_connection(dbname)

    for i in range(toCheck):
        id = resp['result'][i]['id']
        if resp['result'][i]['phase'] != 'FINISHED':
            continue

        try:
            resp2 = requests.get('https://codeforces.com/api/contest.ratingChanges?contestId={0}'.format(id)).json()
        except Exception as e:
            logger.critical(str(e))
            continue
        
        logger.debug('i = {0}; id = {1};'.format(i, id))

        if (resp2['status'] == 'OK' and resp2['result'] == []):
            try:
                contests[id] = min(contests[id] + 1, 2)
            except KeyError:
                contests[id] = 2

            logger.debug('{0} id has been appended'.format(id))
        elif data.execute_read_query(connection, contests_handler.select_id(id)) == [] and resp2['status'] == 'OK':
            skipped.append(id)
            data.execute_query(connection, contests_handler.insert_id(id))

    connection.close()
    logger.debug('updating is done')
    return (contests, skipped)

def check_changes(contests):
    res = list()
    contests2 = contests

    for id in contests.keys():
        try:
            resp = requests.get('https://codeforces.com/api/contest.ratingChanges?contestId={0}'.format(id)).json()
        except Exception as e:
            logger.critical(str(e))
            continue

        logger.debug('for {0} status is {1}'.format(id, resp['status']))
        if resp['status'] == 'OK' and resp['result'] != []:
            res.append(id)
            with data.create_connection(dbname) as connection:
                data.execute_query(connection, contests_handler.insert_id(id))
        elif resp['status'] == 'FAILED':
            logger.warning(resp['comment'])

        contests[id] -= 1
        if contests[id] == 0:
            contests2.pop(id)
            logger.debug('{0} is no longer in the list'.format(id))
    
    logger.debug('{0} contests checked'.format(len(contests)))
    return (res, contests2)

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
            res[resp['result'][i]['handle']] = (resp['result'][i]['oldRating'], resp['result'][i]['newRating'])
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