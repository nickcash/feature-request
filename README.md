[![Build Status](https://travis-ci.org/nickcash/feature-request.svg?branch=master)](https://travis-ci.org/nickcash/feature-request)
# feature-request
Example feature request app.

The backend is a Python WSGI application, and the frontend is purely static content. They can be served with any number of WSGI frameworks and HTTP servers, but I've used gunicorn+nginx (and included sample configs for each). Requires a PostgreSQL database.

## Simple steps to deploy:

* Pull project
* `cp config/config.example.cfg config/config.cfg` and add your database settings to the file.
* `cp config/nginx /etc/nginx/sites-enabled/feature-request` and edit settings to point to the project's path (I've used `/var/www/feature-request` ). You may need to remove `/etc/nginx/sites-enabled/default` . (re)start nginx
* (optional) `pyenv env` and `source env\bin\activate` to create Python virtual environment. Unnecessary on a production server, but wise on a developer box.
* `pip3 install -r requirements.txt` (may require installation of Postgres libpq headers: `apt-get install libpq-dev`)
* `cd src`, `gunicorn app:app --config=../config/gunicorn_config.cfg`
