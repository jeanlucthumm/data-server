# This file is for random one-time shit I had to do with python
import argparse

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


def add_user_to_unowned_tasks_and_task_names(update_task_names=False, update_tasks=False):
    """
    After adding authentication, all the previous tasks and task names were missing user ID.
    This function adds the passed UID to all of them
    """
    parser = argparse.ArgumentParser(description='Claim unowned tasks with given uid')
    parser.add_argument('--cred',
                        help='path to credential json file to authenticate with Firestore',
                        required=True)
    parser.add_argument('--uid', help='user ID', required=True)
    flags = parser.parse_args()

    cred = credentials.Certificate(flags.cred)
    firebase_admin.initialize_app(cred)

    if update_task_names:
        task_names_ref = firebase_admin.firestore.client().collection('DividerTaskNames')
        for doc in task_names_ref.stream():
            data = doc.to_dict()
            if 'userId' in data:
                print(f"Skipping {data['name']}")
                continue
            print(f"Updating {data['name']} with uid {flags.uid}")
            doc.reference.update({'userId': flags.uid})

    if update_tasks:
        tasks_ref = firebase_admin.firestore.client().collection('DividerTasks')
        for doc in tasks_ref.stream():
            data = doc.to_dict()
            if 'userId' in data:
                print(f"Skipping ({data['name']}, {data['startTime']})")
                continue
            print(f"Updating ({data['name']}, {data['startTime']}) with uid {flags.uid}")
            doc.reference.update({'userId': flags.uid})


def strip_whitespace_from_task_names(update_task_names=False, update_tasks=False):
    """
    Forgot to add cleaning to adding task names, so there's extra white space around it
    """
    parser = argparse.ArgumentParser(description='Claim unowned tasks with given uid')
    parser.add_argument('--cred',
                        help='path to credential json file to authenticate with Firestore',
                        required=True)
    flags = parser.parse_args()

    cred = credentials.Certificate(flags.cred)
    firebase_admin.initialize_app(cred)

    if update_task_names:
        task_names_ref = firebase_admin.firestore.client().collection('DividerTaskNames')
        for doc in task_names_ref.stream():
            data = doc.to_dict()
            print(f"Updating {data['name']}")
            doc.reference.update({'name': data['name'].strip()})

    if update_tasks:
        tasks_ref = firebase_admin.firestore.client().collection('DividerTasks')
        for doc in tasks_ref.stream():
            data = doc.to_dict()
            print(f"Updating ({data['name']}, {data['startTime']})")
            doc.reference.update({'name': data['name'].strip()})


if __name__ == '__main__':
    pass
