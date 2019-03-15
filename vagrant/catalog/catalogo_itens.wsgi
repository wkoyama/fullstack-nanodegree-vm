import sys
import os

APP_HOME = r"/home/grader/fullstack-nanodegree-vm/vagrant/catalog"

activate_this = '/home/grader/fullstack-nanodegree-vm/vagrant/catalog/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, APP_HOME)
os.chdir(APP_HOME)

from app import app
application = app