from flask             import Flask
from flask_api         import FlaskAPI
from flask_bcrypt      import Bcrypt
from flask_mongoengine import MongoEngine

from config import Config

app = FlaskAPI(__name__)
app.config.from_object(Config)

db = MongoEngine()
db.init_app(app)

bcrypt = Bcrypt()
bcrypt.init_app(app)

from app import routes
