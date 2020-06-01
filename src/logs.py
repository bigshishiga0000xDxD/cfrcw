import logging
from env import path

logging.basicConfig(filename = path + 'log.log', format = '%(asctime)s %(message)s', filemode = 'w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG) 