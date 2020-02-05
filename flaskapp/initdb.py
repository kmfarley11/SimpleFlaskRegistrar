#######################################################################################
# initdb.py
#	use this file to create/reset a "flaskapp.db"
#	enter the desired admin credentials 
#	and be sure to keep copies of the outputted "salt.txt"
#	this is primarily a local utility used to initialize the flaskapp database
#######################################################################################

import sqlite3
import stdiomask
import bcrypt

# delete db if exists, create new one
conn = sqlite3.connect('flaskapp.db')
cur = conn.cursor()
cur.execute("""DROP TABLE IF EXISTS flaskapp""")
cur.execute("""CREATE TABLE flaskapp
    (username text, password text, firstname text, lastname text, email text)""")

# create admin account on init of db
print 'Enter your admin password here'
admin_pass = stdiomask.getpass(mask='*')

# store salt into a file locally (DO NOT LOSE IT!!!)
salt = bcrypt.gensalt()
with open('salt.txt', 'wc') as f:
    f.write(salt)
hashed = bcrypt.hashpw(admin_pass, salt)

# add the admin account and commit db changes
cur.execute("""INSERT INTO flaskapp VALUES (?,?,?,?,?)""",
    ('admin', hashed, 'admin', 'account', 'admin@notanemail.com'))
conn.commit()
conn.close()

