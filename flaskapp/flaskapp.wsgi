#######################################################################################
# flaskapp.wsgi
#  necessary to serve our flaskapp in modwsgi on a basic aws instance
#  also contains some relevant setup info
#######################################################################################
import sys
sys.path.insert(0, '/var/www/html/flaskapp')

from flaskapp import app as application

########
# NOTES:
#  for this to work, need to have apache2 and mod_wsgi installed
#  in /etc/apache2/sites-available/000-default.conf add the following:
####
#    WSGIDaemonProcess flaskapp threads=5
#    WSGIScriptAlias / /var/www/html/flaskapp/flaskapp.wsgi
#
#    <Directory flaskapp>
#            WSGIProcessGroup flaskapp
#       WSGIApplicationGroup %{GLOBAL}
#        Order deny,allow
#        Allow from all
#    </Directory>
####
# also symbolically link /var/www/html/flaskapp to the directory housing these files
# and ensure the db is writeable by apache:
#   python initdb.py # enter an admin user
#   sudo chmod 664 flaskapp.db
#   sudo chown ubuntu:www-data -R $(pwd)
# some python packages are also necessary:
#   sudo apt-get install python-flask python-bcrypt python-stdiomask
####
# essentially follow the instructions provided: 
#  https://www.datasciencebytes.com/bytes/2015/02/24/running-a-flask-app-on-aws-ec2/
########
