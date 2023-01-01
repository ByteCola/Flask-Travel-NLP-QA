# -*- encoding: utf-8 -*-
"""
Copyright (c) 2022 - 微信 bytecola
"""

from flask import Blueprint

blueprint = Blueprint(
    'chat_blueprint',
    __name__,
    url_prefix=''
)
