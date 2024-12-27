from flask import Flask
from flask_app.controllers import setup_routes
import logging

def create_app():
    """建立 Flask 應用並配置路由"""
    app = Flask(__name__)
    setup_routes(app)
    return app
