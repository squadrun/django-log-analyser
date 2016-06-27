.. image:: https://img.shields.io/pypi/dm/django-log-analyser.svg?maxAge=2592000?style=flat-square   :target: https://pypi.python.org/pypi/django-log-analyser

============
Log Analyser
============

Install pgbadger in Ubuntu
--------------------------

1. Open your source list file::

    sudo nano /etc/apt/sources.list

2. Modify the file to include "yakkety universe" as a source::

    deb http://us.archive.ubuntu.com/ubuntu yakkety universe

3. Update your system::

    sudo apt-get update

4. Install pgbadger::

    sudo apt-get install pgbadger


Quick start
-----------

1. Add apps from "log_analyser" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'log_analyser',
    ]

2. Include the log_analyser URLconf in your project urls.py like this::

    url(r'', include('log_analyser.urls')),

3. "log_analyser" needs you to add a few constants to your settings::

    AWS_REGION = "aws-region"
    BUCKET_LOG_ANALYSER = 'bucket-name'
    RDS_DB_INSTANCE_IDENTIFIER = ['rds-db-instance-identifier-1', 'rds-db-instance-identifier-2' ...]
    AWS_ACCESS_KEY_ID = "aws-access-key"
    AWS_SECRET_ACCESS_KEY = "aws-secret-access-key"

4. Run `python manage.py migrate` to create the log_analyser models.
