import os
import sqlite3
import sys
from urllib.request import pathname2url

from flask import Flask, g, jsonify

app = Flask(__name__)
log = app.logger
DATABASE_URI = None


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        try:
            db = g._database = sqlite3.connect(DATABASE_URI, uri=True)
            log.info('Loaded database with URI: %s', DATABASE_URI)
        except Exception as e:
            log.critical('Failed to get database for URI: %s, with error: %s', DATABASE_URI, e)
            return None
    db.row_factory = sqlite3.Row
    return db


def query_db(query, args=()):
    cursor = get_db().cursor()
    cursor.execute(query, args)
    rows = cursor.fetchall()
    if len(rows) == 0:
        return []
    else:
        return [rows[0].keys()] + [tuple(row) for row in rows]


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = query_db('SELECT * FROM Tasks')
    return jsonify(tasks)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Please prove a database path as the first argument')
    elif not os.path.isfile(sys.argv[1]):
        print('Invalid database path')
    else:
        DATABASE_URI = 'file:{}?mode=rw'.format(pathname2url(sys.argv[1]))
        app.run()
