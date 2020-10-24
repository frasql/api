from models.store import StoreModel
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required


class Store(Resource):
    # parse arguments
    parser = reqparse.RequestParser()
    parser.add_argument(
        "name", type=str, required=True, help="Name of a store is required"
    )
    parser.add_argument(
        "items", type=list, required=True, help="Name of a store is required"
    )

    @jwt_required
    def get(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json()

        return {"message": f"Store with name '{name}' not found "}, 404

    @jwt_required
    def post(self, name: str):
        if StoreModel.find_by_name(name):
            return {"message": f"A store named '{name}' already exists"}, 404

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            {"message": "An error occurred while creating the store"}, 500

        return store.json(), 201

    @jwt_required
    def delete(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()

        return {"message": "Store Deleted Successfully"}

    @jwt_required
    def put(self, name: str):
        store = StoreModel.find_by_name(name)
        if store is None:
            store = StoreModel(name)
        else:
            # store.items = [data['store_id']]

            store.save_to_db()

        return store.json()


class StoreList(Resource):
    @jwt_required
    def get(self):
        return {"stores": [x.json() for x in StoreModel.find_all()]}
