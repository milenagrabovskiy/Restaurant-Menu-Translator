"""module that creates and configures a flask app. errorhandler() is used to handle errors and return consistent responses"""
import time
import uuid
import structlog

from flask import Flask, Response, g, request
from flask_migrate import Migrate
from pydantic import ValidationError

from menu_translator.blueprints.health import health_bp
from menu_translator.blueprints.menu_item_routes import menu_item_bp
from menu_translator.blueprints.restaurant_routes import restaurants_bp


from menu_translator.responses import error_response
from menu_translator.errors import RestaurantManagementError, AWSError
from menu_translator.extensions import db

import os



migrate = Migrate()



def create_app(config: dict | None = None) -> Flask:
    """creates, registers blueprints, and configures a Flask app instance.
    Uses Flask errorhandler() to handle errors centrally"""

    structlog.configure(processors=[structlog.processors.JSONRenderer()])

    logger = structlog.get_logger()

    app = Flask(__name__)


    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())
        g.start_time = time.perf_counter()

    @app.after_request
    def after_request(response: Response):
        duration_ms = (time.perf_counter() - g.start_time) * 1000
        logger.info("completed_request", method=request.method,
                    path=request.path,
                    status_code=response.status_code,
                    duration=round(duration_ms, 3),
                    request_id=g.request_id)
        return response


    # connect to db
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    db.init_app(app)
    migrate.init_app(app, db) #app first then db

    # blueprints
    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(restaurants_bp, url_prefix="/api/v1/restaurants")
    app.register_blueprint(menu_item_bp, url_prefix="/api/v1/restaurants")
    

    # error handlers
    @app.errorhandler(RestaurantManagementError)
    def handle_restaurant_management_error(error: RestaurantManagementError):
        return error_response(error.code, error.status, error.detail)


    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        first_error = error.errors()[0]
        location = first_error['loc']
        field = location[0] if location else "request"
        detail_str = f"{field}:{first_error['msg']}"
        return error_response("validation_failed", 422, detail_str)

    @app.errorhandler(AWSError)
    def handle_aws_error(error: AWSError):
        return error_response(error.code, error.status, error.detail)

    @app.errorhandler(404)
    def handle_not_found_error(error):
        return error_response(code="resource_not_found", status=404, detail="The requested resource does not exist")


    return app
