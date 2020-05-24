import requests
import json

from logs import logger

def detect_div(s):
    if 'Div. 3' in s:
        return 3
    elif 'Educational' in s or 'Div. 2' in s:
        return 2
    else:
        return 1

def update_contests():
    try:
        resp = requests.get('https://codeforces.com/api/contest.list?gym=false').json()
    except Exception as e:
        logger.critical(str(e))
        return dict()

    if resp['status'] != 'OK':
        logger.error('looks like cf is down')
        return dict()
    
    contests = dict()
    for i in range(10):
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
            res.append(resp['result'][0]['contestName'])
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
        return -1
    
    if resp['status'] == 'OK':
        return 1
    elif resp['comment'] == 'handles: User with handle {0} not found'.format(handle):
        return 0
    else:
        return -1

def get_contestants(id):
    resp = requests.get('https://codeforces.com/api/contest.ratingChanges?contestId={0}'.format(id)).json()
    if resp['status'] == 'FAILED':
        logger.critical(resp['comment'])
        return None
    else:
        res = dict()
        for i in range(len(resp['result'])):
            res[resp['result'][i]['handle']] = (resp['result'][i]['oldRating'], resp['result'][i]['newRating'])
        return (res, resp['result'][0]['contestName'])
