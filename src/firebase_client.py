from google.cloud import firestore


def get_db():
    return firestore.Client()
