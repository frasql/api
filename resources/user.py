from flask import request
from blacklist import BLACKLIST
from flask_restful import Resource
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)

from marshmallow import ValidationError
from models.user import UserModel
from schemas.user import UserSchema


NAME_ALREADY_EXISTS = "An user with name '{}' already exists"
ERROR_INSERTING = "An error occurred inserting user"
USER_NOT_FOUND = "User not found"
USER_CREATED = "User Created Successfully"
USER_DELETED = "User Successfully Deleted"
USER_LOGOUT = "User <id={}> successfully logged out"
INVALID_CREDENTIALS = "Invalid Credentials"
NOT_CONFIRMED_ERROR = (
    "You have not confirmed registration, please check your email <{}>."
)


user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        # get data from request to schema
        user_json = request.get_json()
        # propogate exception
        user = user_schema.load(user_json)

        if UserModel.find_by_username(user.username):
            {"message": NAME_ALREADY_EXISTS.format(user.username)}, 400

        try:
            user.save_to_db()
        except:
            return {"message": ERROR_INSERTING}, 500

        return {"message": USER_CREATED}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from request to schema
        user_json = request.get_json()
        # propogate exception
        user_data = user_schema.load(user_json)
        # find user in db
        user = UserModel.find_by_username(user_data.username)

        # check password -> `authenticate()`
        if user and safe_str_cmp(user.password, user_data.password):
            # mail confirm
            if user.activated:
                # create access token -> `identity()`
                access_token = create_access_token(identity=user.id, fresh=True)
                # create refresh token
                refresh_token = create_refresh_token(user.id)
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }, 200
            return {"message": NOT_CONFIRMED_ERROR.format(user.username)}, 400

        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jwt id
        BLACKLIST.add(jti)
        user_id = get_jwt_identity()
        return {"message": USER_LOGOUT.format(user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200


class UserConfirm(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        # change email confirmation
        user.activated = True
        try:
            user.save_to_db()
            return {"message": USER_CREATED}, 200
        except:
            return {"message": ERROR_INSERTING}, 500
