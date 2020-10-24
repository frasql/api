from models.store import StoreModel
from flask_restful import Resource
from flask_jwt_extended import jwt_required


NAME_ALREADY_EXISTS = "A store with name '{}' already exists"
ERROR_CREATING = "An error occurred creating store"
STORE_NOT_FOUND = "Store not found"
STORE_DELETED = "Store Successfully Deleted"


class Store(Resource):
    @classmethod
    @jwt_required
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()

        return {"message": STORE_NOT_FOUND}, 404

    @classmethod
    @jwt_required
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {"message": NAME_ALREADY_EXISTS}, 404

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            {"message": ERROR_CREATING}, 500

        return store.json(), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {"message": STORE_DELETED}

    @classmethod   
    @jwt_required
    def put(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store is None:
            store = StoreModel(name)
        else:
            # store.items = [data['store_id']]

            store.save_to_db()

        return store.json()


class StoreList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        return {"stores": [store.json() for store in StoreModel.find_all()]}
