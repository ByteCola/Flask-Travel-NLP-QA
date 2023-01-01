# -*- encoding: utf-8 -*-

import pymongo
from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from database import Database
from authentication import blueprint
from authentication.forms import LoginForm, CreateAccountForm
from authentication.models import Users
from authentication.util import verify_pass

# from run_flask import login_manager
from run_flask import login_manager


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        database = Database()
        user_col = database.get_collection('sight_qa_db', 'user_data')
        user_data = user_col.find_one({"username": username})
        user = None
        if user_data:
            user = Users(**user_data)

        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               segment='login',
                               msg='Wrong user or password',
                               form=login_form)

    #  or not current_user.is_authenticated
    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               segment='login',
                               form=login_form)
    return redirect(url_for('chat_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        database = Database()
        user_col = database.get_collection('sight_qa_db', 'user_data')
        user = user_col.find_one({"username": username})

        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   segment='register',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = user_col.find_one({"email": email})
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   segment='register',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user

        user = {'username': request.form.get("username"), 'password': request.form.get("password"),
                'email': request.form.get("email")}
        user_col.insert_one(user)

        return render_template('accounts/register.html',
                               msg='User created please <a href="/login">login</a>',
                               segment='register',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html',
                               segment='register',
                               form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    # return render_template('page-403.html'), 403
    return redirect(url_for('authentication_blueprint.login'))


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500
