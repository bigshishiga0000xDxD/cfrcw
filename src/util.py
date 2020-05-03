import requests
import json

from logs import logger

def update_contests():
    try:
        resp = requests.get('https://codeforces.com/api/contest.list?gym=false').json()
    except Exception as e:
        logger.critical(str(e))
        return list()

    if resp['status'] != 'OK':
        logger.error('looks like cf is down')
        return list()
    
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
            logger.debug(resp['comment'])

        contests[id] -= 1
        if contests[id] == 0:
            contests.pop(id)
            logger.debug('{0} is no longer in the list'.format(id))
        
    
    logger.debug('{0} contests checked'.format(len(contests)))
    return res