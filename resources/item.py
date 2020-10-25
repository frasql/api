from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    jwt_optional,
    get_jwt_identity,
    fresh_jwt_required,
)

from marshmallow import ValidationError
from schemas.item import ItemSchema
from models.item import ItemModel


NAME_ALREADY_EXISTS = "An item with name '{}' already exists"
ERROR_INSERTING = "An error occurred inserting item"
ADMIN_REQUIRED = "Admin privileges required."
ITEM_NOT_FOUND = "Item not found"
ITEM_DELETED = "Item Successfully Deleted"
DATA_AVAILABLE = "More data available if you log in."


item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    @jwt_required
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item)
        else:
            return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"message": NAME_ALREADY_EXISTS.format(name)}, 400

        item_json = request.get_json()
        item_json["name"] = name  # /item/name

        # propogate exception
        item = item_schema.load(item_json)

        try:
            item.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return item_schema.dump(item), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"message": ADMIN_REQUIRED}, 401
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {"message": ITEM_DELETED}

    @classmethod
    @jwt_required
    def put(cls, name: str):
        item_json = request.get_json()
        item = ItemModel.find_by_name(name)

        if item:
            item.price = item_json["price"]
        else:
            item_json["name"] = name

            # propogate exception
            item = item_schema.load(item_json)

        item.save_to_db()

        return item_schema.dump(item), 200


class ItemList(Resource):
    @classmethod
    @jwt_optional
    def get(cls):
        user_id = get_jwt_identity()
        items = item_list_schema.dump(ItemModel.find_all())
        if user_id:
            return {"items": items}, 200
        return {
            "items": "",
            "message": DATA_AVAILABLE,
        }, 200
