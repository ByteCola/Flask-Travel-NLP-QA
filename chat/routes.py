# -*- encoding: utf-8 -*-
"""
Copyright (c) 2022 - 微信 bytecola
"""
import json
import os

from flask_login import login_required

from chat import blueprint
from flask import render_template, request, redirect, url_for
from jinja2 import TemplateNotFound

import qa.qabase as qa


@blueprint.route('/')
def route_default():
    """
    网站访问默认跳转至index首页
    :return:
    """
    return redirect(url_for('chat_blueprint.index'))


@blueprint.route('/index')
@login_required
def index():
    return render_template('chat/index.html', segment='index')


# 问答api
@blueprint.route('/qa')
@login_required
def question_answer():
    sentence = request.args.get('q')
    algorithm = request.args.get('algorithm')
    # global answerer
    answerer = qa.Answerer()
    response, sim = answerer.get_response(sentence, algorithm)
    threshold = 0
    datas = {}
    if sim > threshold:
        datas = {"answer": response, "sim": sim}
        print(response)
    return {"success": True,
            "msg": "query successed",
            "datas": datas}


# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
