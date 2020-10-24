from typing import Dict, List, Union
from db import db


UserJSON = Dict[str, Union[int, str]]


class UserModel:
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def json(self) -> UserJSON:
        return {"id": self.id, "uername": self.username}

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        user = cls.query.filter_by(username=username).first()
        return user

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        user = cls.query.filter_by(id=_id).first()
        return user

    @classmethod
    def find_all(cls) -> List["UserModel"]:
        return cls.query.all()
