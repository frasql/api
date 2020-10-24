from blacklist import BLACKLIST
from flask import Flask
import jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from blacklist import BLACKLIST
from db import db


# flask config
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
app.secret_key = "1Passwd1"
# api
api = Api(app)
# sqlalchemy
db.init_app(app)
# create table
@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)  # app.config['JWT_SECRET_KEY']


# allow additional data in users payloads
@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {"is_admin": True}
    return {"is_admin": False}


# check if an id is in the blacklist
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return (
        jsonify({"description": "The token has expired.", "error": "token_expired"}),
        401,
    )


# token in header is not a jwt format
@jwt.invalid_token_loader
def invalid_token_callback():
    return (
        jsonify({"description": "Invalid format token.", "error": "invalid_token"}),
        401,
    )


# jwt not received
@jwt.unauthorized_loader
def missing_token_callback():
    return (
        jsonify(
            {"description": "Send a jwt token.", "error": "authorization_required"}
        ),
        401,
    )


# fresh_jwt_required
@jwt.needs_fresh_token_loader
def needs_fresh_token_callback():
    return (
        jsonify(
            {"description": "Fresh token required.", "error": "fresh_token_required"}
        ),
        401,
    )


# revoke a jwt token
@jwt.revoked_token_loader
def revoked_token_callback():
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
    )


# application endpoints
api.add_resource(Item, "/item/<string:name>/")
api.add_resource(ItemList, "/items/")
api.add_resource(StoreList, "/stores/")
api.add_resource(Store, "/stores/<string:name>")
api.add_resource(UserRegister, "/register/")
api.add_resource(User, "/user/<int:user_id>/")
api.add_resource(UserLogin, "/login/")
api.add_resource(UserLogout, "/logout/")
api.add_resource(TokenRefresh, "/refresh/")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
