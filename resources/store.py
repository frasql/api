from flask import request
from models.store import StoreModel
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from marshmallow import ValidationError
from schemas.store import StoreSchema


NAME_ALREADY_EXISTS = "A store with name '{}' already exists"
ERROR_CREATING = "An error occurred creating store"
STORE_NOT_FOUND = "Store not found"
STORE_DELETED = "Store Successfully Deleted"


store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    @jwt_required
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store), 200

        return {"message": STORE_NOT_FOUND}, 404

    @classmethod
    @jwt_required
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {"message": NAME_ALREADY_EXISTS}, 404

        store = StoreModel(name=name)

        try:
            store.save_to_db()
        except:
            {"message": ERROR_CREATING}, 500

        return store_schema.dump(store), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {"message": STORE_DELETED}, 200


class StoreList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        return {"stores": store_list_schema.dump(StoreModel.find_all())}, 200
