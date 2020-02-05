# SimpleFlaskRegistrar
A basic flask webserver intended for use with an AWS EC2 instance for academic reasons

Designed to address an assignment from Cloud Computing for graduate studies at UC (Spring 2020)

The flask web app is all stored in `./flaskapp`


## Installation
```bash
# assuming linux (debian-based) development environment
sudo apt-get install python python-pip
pip install --user -U pip
pip install --user flask bcrypt stdiomask

# NOTE: if using mod_wsgi on a server, may need to install via apt-get rather than pip
# TODO: support a virtual environment or containers to avoid this...
# sudo apt-get install python python-flask python-bcrypt python-stdiomask
# for more details on a deployment see flaskapp.wsgi...
```

## Usage
```bash
# init the db: provide admin password (only needed once)
python initdb.py

# (optional) verify the db
python check_pass.py

# start the webserver
python flaskapp.py
```
- access the listed IP/port (`127.0.0.1:5000` by default) from your web browser
- enter a new or existing username/password
  - if new, enter registration details (fullname, email)
  - if existing and valid password, will view user details
