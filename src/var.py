from os import environ

# telebot token
token = environ['TOKEN']

# database password
password = environ['PASSWORD']

# database name
dbname = 'cfrcw'

# database user
user = 'postgres'

# size of the group passed to cf api
groupSize = 100

# number of seconds between ratings changes checking
interval = 60

# maximum number of handles stored for one chat
limit = 200

# maximum number of extra handles that are potentially stored 
maximumExtraHandles = 100

maxTime = 86400
