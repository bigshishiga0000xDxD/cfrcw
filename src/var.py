from os import environ

token = environ['TOKEN']        # telebot token
password = environ['PASSWORD']  # database password
dbname = 'cfrcw'                # database name
user = 'postgres'               # database user
groupSize = 100                 # size of the group passed to cf api
toCheck = 10                    # number of contests checked
interval = 60                   # number of seconds between ratings changes checking
limit = 200                     # maximum number of handles stored for one chat
maximumExtraHandles = 100       # maximum number of extra handles that are potentially stored 
