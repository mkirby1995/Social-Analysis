"""Entry Point for Social Network Analysis"""

from .app import create_app
from flask_sqlalchemy import SQLAlchemy
from .models import DB, User, Tweet
from .twitter import add_user, add_users

DB = SQLAlchemy()
APP = create_app()
