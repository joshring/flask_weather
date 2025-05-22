from flask import Flask, json
from werkzeug.exceptions import HTTPException


def create_app() -> Flask:
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    @app.errorhandler(HTTPException)
    def handle_exception(err):
        """
        Return JSON instead of HTML for HTTP errors.
        """
        # start with the correct headers and status code from the error
        response = err.get_response()
        # replace the body with JSON
        response.data = json.dumps(
            {
                "code": err.code,
                "name": err.name,
                "description": err.description,
            }
        )
        response.content_type = "application/json"
        return response

    # Add blueprints
    from app.weather import bp as weather_bp

    app.register_blueprint(weather_bp)

    return app
