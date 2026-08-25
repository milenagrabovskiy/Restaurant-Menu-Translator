from flask import Flask
from flask_migrate import Migrate
from pydantic import ValidationError

from menu_translator.blueprints.health import health_bp
from menu_translator.blueprints.menu_items import menu_item_bp
from menu_translator.blueprints.restaurants import restaurants_bp
from menu_translator.models.db_models.menu_item_orm import MenuItemRecord
from menu_translator.models.db_models.restaurant_orm import RestaurantRecord

from menu_translator.extensions import db

import os



migrate = Migrate()



def create_app():

    app = Flask(__name__)

    # connect to db
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    db.init_app(app)
    migrate.init_app(app, db) #app first then db


    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(restaurants_bp, url_prefix="/api/v1/restaurants")
    app.register_blueprint(menu_item_bp, url_prefix="/api/v1/menu_items")

    return app