from api.v1 import backend

def disable_all_group():
    db = backend.DBBackend.default()
    db.disable_all_group()