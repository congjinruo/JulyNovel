"""
The flask application package.
"""
# -*- coding: utf-8 -*-
from flask import Flask
from flask_caching import Cache

create_app = Flask(__name__)
# Check Configuring Flask-Cache section for more details
cache = Cache(create_app,config={'CACHE_TYPE': 'simple'})
import app.views