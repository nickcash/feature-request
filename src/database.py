"""Database connection manager"""

import configparser
import psycopg2
import psycopg2.extras


config = configparser.ConfigParser()
config.read("../config/config.cfg")

connection = psycopg2.connect(
    host=config.get("database", "host"),
    port=config.get("database", "port", fallback=5432),
    database=config.get("database", "database"),
    user=config.get("database", "username"),
    password=config.get("database", "password"),

    # Return results as dict
    cursor_factory=psycopg2.extras.RealDictCursor,
)

# No need for transactions in this app
connection.set_session(autocommit=True)
