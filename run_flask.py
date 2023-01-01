# -*- encoding: utf-8 -*-

"""
Copyright (c) 2022 - 微信 bytecola
"""
from importlib import import_module

from flask import Flask
from flask_login import LoginManager

login_manager = LoginManager()


def register_blueprints(app):
    print("##### load module route ###")
    # chat_module = import_module('chat.routes')
    # app.register_blueprint(chat_module.blueprint)
    # authentication_module = import_module('authentication.routes')
    #
    #
    #
    # app.register_blueprint(authentication_module.blueprint)
    for module_name in (
            'authentication', 'chat'):
        module = import_module('{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def register_extensions(app):
    login_manager.init_app(app)



def create_app():
    print("execute create_app function ...........")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'S#perSTcrEt_2437'
    register_blueprints(app)
    register_extensions(app)
    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
