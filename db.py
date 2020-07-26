from firebase_admin import credentials
from firebase_admin import firestore

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


def create_default_tables(cursor):
    cursor.execute('''
        CREATE TABLE Tasks(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            startTime INTEGER NOT NULL
        )
    ''')


def default_tables_exist(cursor):
    cursor.execute('''
        SELECT count(name)
        FROM sqlite_master
        WHERE type='table' AND name='Tasks'
    ''')
    return cursor.fetchone()[0] == 1


def get_last_start_time(cursor):
    cursor.execute('''
        SELECT max(startTime) FROM Tasks
    ''')
    res = cursor.fetchone()
    if res is None or res[0] is None:
        return 0
    else:
        return res[0]


def add_task(cursor, name, start_time):
    log.info('Adding task: name(%s), startTime(%d)', name, start_time)
    cursor.execute('''
        INSERT INTO Tasks VALUES (NULL, ?, ?)
    ''', (name, start_time))


def update_db(tasks_ref, db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if not default_tables_exist(c):
        create_default_tables(c)
    last_time = get_last_start_time(c)
    count = 0
    for doc in tasks_ref.where('startTime', '>', last_time).stream():
        add_task(c, doc.get('name'), doc.get('startTime'))
        count += 1
    conn.commit()
    after_last_time = get_last_start_time(c)
    log.info('Added %d tasks', count)
    log.info('Prev last time: %d, current last time: %d',
             last_time, after_last_time)


if __name__ == '__main__':
    cred = credentials.Certificate(sys.argv[1])
    firebase_admin.initialize_app(cred)
    update_db(firebase_admin.firestore.client().collection('DividerTasks'),
              sys.argv[2])
