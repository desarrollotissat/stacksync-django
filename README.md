manager
=======

StackSync user manager


To create the database tables:
manage.py syncdb

Better update your current working stacksync database with:
ALTER TABLE workspace_user add column id uuid;

To install requirements necessary for the project to run:
pip install -r requirements.txt
