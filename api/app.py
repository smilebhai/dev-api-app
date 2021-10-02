from logging import Logger, basicConfig, INFO
from flask import Flask, Blueprint
from flask_restx import Api, Resource
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from settings import FLASK_DEBUG, FLASK_ENV, SERVICES, RESTPLUS_MASK_SWAGGER, \
    RESTX_ERROR_404_HELP, RESTPLUS_SWAGGER_UI_DOC_EXPANSION
from routes.ratelimits import ns as ns_ratelimits
from routes.services import ns as ns_services
from routes.tasks import ns as ns_tasks

# configure root logger
basicConfig(level=INFO)

# instantiate a Flask application object
flask_app = Flask(__name__)

flask_app.config['FLASK_DEBUG'] = FLASK_DEBUG
flask_app.config['FLASK_ENV'] = FLASK_ENV
flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = \
    RESTPLUS_SWAGGER_UI_DOC_EXPANSION
flask_app.config['RESTPLUS_MASK_SWAGGER'] = RESTPLUS_MASK_SWAGGER
flask_app.config['RESTX_ERROR_404_HELP'] = RESTX_ERROR_404_HELP

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY',
        'description': "Type in the *'Value'* input box below: \
            **'YOUR ACCESS TOKEN'**"
    }
}

# Define a blueprint of how to construct or extend an application
blueprint = Blueprint('api', __name__, url_prefix='/api')

# set limiter configs
limiter = Limiter(
    flask_app,
    key_func=get_remote_address
)

limiter.limit("200/day;50/hour;5/minute", error_message='ratelimit exceeded')(blueprint)

api_desc = "Look up information from {}".format(SERVICES)

# Initialize
api = Api(blueprint,
          version="1.0.0",
          title="API Lookup Service",
          description=api_desc,
          authorizations=authorizations,
          doc='/docs/')

# registers resources from namespace for current instance of api
api.add_namespace(ns_ratelimits)
api.add_namespace(ns_services)
api.add_namespace(ns_tasks)

# Register a blueprint on an application
flask_app.register_blueprint(blueprint)
