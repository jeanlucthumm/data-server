from firebase_admin import credentials
from firebase_admin import firestore

import argparse
import firebase_admin
import sys
import sqlite3
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


def get_all_tasks(db_path):
    conn = _default_connection(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM Tasks')
    return c.fetchall()


def _get_last_start_time(cursor):
    cursor.execute('''
        SELECT max(startTime) FROM Tasks
    ''')
    res = cursor.fetchone()
    if res is None or res[0] is None:
        return 0
    else:
        return res[0]


def _add_task(cursor, name, start_time):
    log.info('Adding task: name(%s), startTime(%d)', name, start_time)
    cursor.execute('''
        INSERT INTO Tasks VALUES (NULL, ?, ?)
    ''', (name, start_time))


def _default_connection(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if not _default_tables_exist(c):
        _create_default_tables(c)
    conn.row_factory = sqlite3.Row
    return conn


def _create_default_tables(cursor):
    cursor.execute('''
        CREATE TABLE Tasks(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            startTime INTEGER NOT NULL
        )
    ''')


def _default_tables_exist(cursor):
    cursor.execute('''
        SELECT count(name)
        FROM sqlite_master
        WHERE type='table' AND name='Tasks'
    ''')
    return cursor.fetchone()[0] == 1


def _update_db(tasks_ref, db_path):
    conn = _default_connection(db_path)
    c = conn.cursor()
    last_time = _get_last_start_time(c)
    count = 0
    for doc in tasks_ref.where('startTime', '>', last_time).stream():
        _add_task(c, doc.get('name'), doc.get('startTime'))
        count += 1
    conn.commit()
    after_last_time = _get_last_start_time(c)
    log.info('Added %d tasks', count)
    log.info('Prev last time: %d, current last time: %d',
             last_time, after_last_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Update local SQL database with information from Firestore')
    parser.add_argument('--cred',
                        help='path to credential json file to authenticate with Firestore',
                        required=True)
    parser.add_argument('--uid', help='user ID (ask Jean-Luc for it)', required=True)
    parser.add_argument('--dbpath', help='path for SQL database to create or update',
                        required=True)
    flags = parser.parse_args()

    cred = credentials.Certificate(flags.cred)
    firebase_admin.initialize_app(cred)
    _update_db(firebase_admin.firestore.client().collection('DividerTasks'),
               flags.dbpath)
