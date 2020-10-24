from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    jwt_optional,
    get_jwt_identity,
    fresh_jwt_required,
)

from models.item import ItemModel


class Item(Resource):
    # parsing arguments
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price", type=float, required=True, help="This field cannot be left blank"
    )
    parser.add_argument(
        "store_id", type=int, required=True, help="Every item needs a store id"
    )

    @jwt_required
    def get(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        else:
            return {"message": "Item not found"}, 404

    @fresh_jwt_required
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return {"message": "Am item with name '{}' exists".format(name)}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting item"}, 500

        return item, 201

    @jwt_required
    def delete(self, name: str):
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"message": "Admin privileges required."}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {"message": "Item Successfully Deleted"}

    @jwt_required
    def put(self, name: str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data["price"]

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {"items": items}, 200
        return {
            "items": [item["name"] for item in items],
            "message": "More data available if you log in.",
        }, 200
