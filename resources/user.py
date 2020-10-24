from blacklist import BLACKLIST
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)

from models.user import UserModel


_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help="The username is required"
                          )
_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help="Password is required"    
                          )


class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()
        if UserModel.find_by_username(data['username']):
            {"message": "Usename: {} already exists.".format(data['user'])}, 400
        
        try:
            user = UserModel(**data)
            user.save_to_db()
        except:
            return {"message": "Error occured inserting user"}

        
        return {"message": "User Created Successfully"}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': "User not found"}, 404
        return user.json()


    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': "User not found"}, 404
        user.delete_from_db()
        return {'message': "User Deleted"}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from parser
        data = _user_parser.parse_args()
        # find user in db
        user = UserModel.find_by_username(data['username'])
        # check password -> `authenticate()`
        if user and safe_str_cmp(user.password, data['password']):
            # create access token -> `identity()`
            access_token = create_access_token(identity=user.id, fresh=True) 
            # create refresh token
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        
        return {"message": "Invalid Credentials"}, 401
        

class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti'] # jwt id
        BLACKLIST.add(jti)
        return {'message': 'Successfully loggged out.'}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
