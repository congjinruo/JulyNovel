"""
Routes and views for the flask application.
"""
# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_graphql import GraphQLView
from .data.base import db_session
from .data.schema import schema
from app import create_app as app
from app import cache
from flask_cors import CORS
from .services.spider import Spider
import threading, time

CORS(app, supports_credentials=True)


@app.teardown_appcontext
def shutdown_session(exception=None):
    cache.clear()
    db_session.remove()


app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql = True, context={'session': db_session}))

@app.route('/')
def index():

    return 'Hello J.Kuai'

@app.route('/missionStart')
def missionStart():
    i = 0
    while(i < 50):
        i += 1
        t = threading.Thread(target=Spider().run, name='spiderMission %s' % i)
        si = threading.Thread(target=Spider().insert, name='insertMission %s' % i)

        t.start()
        si.start()

    sc = threading.Thread(target=Spider().timerStart, name='checkFinish')
    sc.start()

    return 'Mission Start ... '