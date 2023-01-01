# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - 微信 bytecola
"""

import os
import hashlib
import binascii

# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/



def verify_pass(provided_password, stored_password):
    """Verify a stored password against one provided by user"""
    return provided_password == stored_password
