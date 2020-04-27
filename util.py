import requests
import json

from logs import logger

def update_contests():
    try:
        resp = requests.get('https://codeforces.com/api/contest.list?gym=false').json()
    except:
        logger.critical('CONNECTION ERROR !!!!!!!!')
        return list()

    if resp['status'] != 'OK':
        logger.error('looks like cf is down')
        return list()
    else:
        logger.debug('Contest list has been received successfully')
    
    contests = list()
    for i in range(10):
        id = resp['result'][i]['id']
        if resp['result'][i]['phase'] != 'FINISHED':
            continue

        try:
            resp2 = requests.get('https://codeforces.com/api/contest.ratingChanges?contestId={0}'.format(id)).json()
        except:
            logger.critical('CONNECTION ERROR !!!!!!!!')
            continue
        
        logger.debug('i = {0}; id = {1};'.format(i, id))

        if resp2['status'] == 'OK' and resp2['result'] == []:
            contests.append(id)
            logger.debug('{0} id has been appended'.format(id))

    logger.debug('updating is done')
    return contests

def check_changes(contests):
    res = list()
    for id in contests:
        try:
            resp = requests.get('https://codeforces.com/api/contest.ratingChanges?contestId={0}'.format(id)).json()
        except:
            logger.critical('CONNECTION ERROR !!!!!!!!')
            continue

        logger.debug('for {0} status is {1}'.format(id, resp['status']))
        if resp['status'] == 'OK' and resp['result'] != []:
            res.append(resp['result'][0]['contestName'])
        elif resp['status'] == 'FAILED':
            logger.debug(resp['comment'])
    
    logger.debug('{0} contests checked'.format(len(contests)))
    return res
