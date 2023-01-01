# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - 微信 bytecola
"""
from bson import ObjectId
from flask_login import UserMixin

from database import Database
from run_flask import login_manager


class Users(UserMixin):

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            # if property == '_id':
            #     value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

    def get_id(self):
        print(self)
        object_id = self._id
        return str(object_id)

@login_manager.user_loader
def user_loader(id):
    print("########################################")
    print(id)
    database = Database()
    user_col = database.get_collection('sight_qa_db', 'user_data')
    user_data = user_col.find_one({"_id": ObjectId(id)})
    if user_data:
        user = Users(**user_col.find_one({"_id": ObjectId(id)}))
        return user
    else:
        return None


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    database = Database()
    # user = Users.query.filter_by(username=username).first()
    user_col = database.get_collection('sight_qa_db', 'user_data')

    user = user_col.find_one({"username": username})

    return user if user else None

