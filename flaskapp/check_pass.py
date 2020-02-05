#######################################################################################
# check_pass.py
#	can be used to verify a user's login against flaskapp.db locally
#	not for use with flask, just a local utility
#######################################################################################
import sqlite3
import stdiomask
import bcrypt


# connect to db
conn = sqlite3.connect('flaskapp.db')
cur = conn.cursor()
# tbl = cur.execute('SELECT * FROM flaskapp')
# u,h,f,l,e = tbl.fetchall()[0]


# create admin account on init of db
usr = raw_input('Enter a user to check here: ')
u_db = cur.execute('SELECT * FROM flaskapp WHERE username=?', (usr,))
res = u_db.fetchall()

if not res:
    print 'Error, user %s not found!' % (usr)
    exit(1)
elif len(res) > 1:
    print 'Error, more than one user found!'
    exit(1)

print "Enter the %s's password here" % (usr)
admin_pass = stdiomask.getpass(mask='*')

# read salt and use to check password
salt = ''
with open('salt.txt', 'r') as f:
    salt = f.read()
hashed = bcrypt.hashpw(admin_pass, salt)

# verify the password then close db connection
if hashed != res[0][1]:
    print 'Error, password specified was incorrect!'
else:
    print 'Authenticated!'
conn.commit()
conn.close()
