import firebase_admin
import sys
from firebase_admin import credentials
from firebase_admin import firestore

if __name__ == '__main__':
    cred = credentials.Certificate(sys.argv[1])
    firebase_admin.initialize_app(cred)
    fire = firebase_admin.firestore.client()
    taskNames = fire.collection('DividerTaskNames')
    for doc in taskNames.list_documents():
        print(doc.get().to_dict())
