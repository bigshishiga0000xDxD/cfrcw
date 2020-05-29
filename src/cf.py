import requests
import json

from logs import logger
from auth import make_query

def update_contests(toCheck = 10):
    try:
        resp = requests.get('https://codeforces.com/api/contest.list?gym=false').json()
    except Exception as e:
        logger.critical(str(e))
        return dict()

    if resp['status'] == 'FAILED':
        logger.critical('looks like cf is down')
        return dict()
    
    contests = dict()
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

        if resp2['status'] == 'OK' and resp2['result'] == []:
            try:
                contests[id] += 1
            except KeyError:
                contests[id] = 2

            logger.debug('{0} id has been appended'.format(id))

    logger.debug('updating is done')
    return contests

def check_changes(contests):
    res = list()
    for id in contests.keys():
        try:
            resp = requests.get('https://codeforces.com/api/contest.ratingChanges?contestId={0}'.format(id)).json()
        except Exception as e:
            logger.critical(str(e))
            continue

        logger.debug('for {0} status is {1}'.format(id, resp['status']))
        if resp['status'] == 'OK' and resp['result'] != []:
            res.append(id)
        elif resp['status'] == 'FAILED':
            logger.warning(resp['comment'])

        contests[id] -= 1
        if contests[id] == 0:
            contests.pop(id)
            logger.debug('{0} is no longer in the list'.format(id))
        
    
    logger.debug('{0} contests checked'.format(len(contests)))
    return res

def check_user(handle):
    try:
        resp = requests.get('https://codeforces.com/api/user.info?handles={0}'.format(handle)).json()
    except Exception as e:
        logger.critical(str(e))
        return (-1, None)
    
    if resp['status'] == 'OK':
        return (1, resp['result'][0]['handle'])
    elif resp['comment'] == 'handles: User with handle {0} not found'.format(handle):
        return (0, None)
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
    args = make_query({'onlyOnline': 'false'}, 'user.friends', open, secret)
    url = 'https://codeforces.com/api/user.friends?'

    for i in range(len(args)):
        url += args[i][0]
        url += '='
        url += args[i][1]
        if (i != len(args) - 1):
            url += '&'
    
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