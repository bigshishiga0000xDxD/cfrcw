from random import choice
from time import time
from hashlib import sha512


chars = [chr(i) for i in range(97, 97 + 26)] + [str(i) for i in range(10)]

def randstr(len = 6):
    res = str()
    for _ in range(len):
        res += choice(chars)
    return res

def make_query(args, methodName, open, secret):
    args['apiKey'] = open
    args['time'] = str(round(time()))

    args = sorted(args.items())

    rand = randstr()
    apiSig = rand + '/' + methodName + '?'
    for i in range(len(args)):
        apiSig += args[i][0]
        apiSig += '='
        apiSig += args[i][1]
        if i != len(args) - 1:
            apiSig += '&'
    
    apiSig += '#'
    apiSig += secret

    hash = sha512(apiSig.encode('utf-8'))
    args.append(('apiSig', rand + hash.hexdigest()))

    url = 'https://codeforces.com/api/{0}?'.format(methodName)

    for i in range(len(args)):
        url += args[i][0]
        url += '='
        url += args[i][1]
        if (i != len(args) - 1):
            url += '&'
    
    return url
