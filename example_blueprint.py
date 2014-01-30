# -*- coding: utf-8 -*-

from flask import Flask, Blueprint, views, current_app, jsonify
from flask_restful import fields, Api, abort
from flask_restful_swagger import swagger

ALERTS = {
    1: {
        'id': 1,
        'name': 'First',
        'active': True,
        'field': 'hidden'
    },
    2: {
        'id': 1,
        'name': 'Second',
        'active': False,
        'field': 'hidden'
    }
}


@swagger.model
class Alert:
    resource_fields = {
        "id": fields.Integer,
        "name": fields.String,
        "frequency": fields.Fixed,
        "active": fields.Boolean,
    }


def json_response_decorator(f):
    '''Presents `dict`, `list`, cursor or any iterable object as JSON.
    Creates `~flask.Response` object and sets headers.
    It also handles exceptions and raises proper HTTP exceptions
    in a JSON format.
    '''
    def decorator(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
        except Exception as e:
            current_app.logger.exception(e)
            raise
        return jsonify(result)
    return decorator


class RestView(views.MethodView):
    # make converter run after every request handler method returns
    # !!! Order is important: decorators are called last to first
    decorators = [json_response_decorator]


class AlertsEndpoint(RestView):
    @swagger.operation(
        notes='Create a new alert',
        responseClass=Alert.__name__,
        parameters=[
            {
                "name": "body",
                "description": "An Alert item",
                "required": True,
                "allowMultiple": False,
                "dataType": Alert.__name__,
                "paramType": "body"
            }
        ],
        responseMessages=[
            {
                "code": 201,
                "message": "Created alert"
            },
            {
                "code": 405,
                "message": "Invalid input"
            }
        ]
    )
    def post(self):
        """ Create a new funnel
        """
        pass


class AlertEndpoint(RestView):
    """ Individual alerts used to notify a user
    """

    @swagger.operation(
        notes='Get a specific alert',
        responseClass=Alert.__name__,
        parameters=[
            {
                "name": "alert_id",
                "description": "The ID of the alert to be retrieved",
                "required": True,
                "allowMultiple": False,
                "dataType": "integer",
                "paramType": "path"
            }
        ],
        responseMessages=[
            {
                "code": 405,
                "message": "Bad Alert ID"
            }
        ]
    )
    def get(self, alert_id):
        """ Get a specific alert
        """
        if alert_id not in ALERTS:
            abort(404, alert_id=alert_id)
        return ALERTS[alert_id]


    @swagger.operation(
        notes='Patch a specific alert',
        responseClass=Alert.__name__,
        parameters=[
            {
                "name": "name",
                "description": "The new name for the alert",
                "required": False,
                "allowMultiple": False,
                "dataType": "string",
                "paramType": "form"
            }
        ],
        responseMessages=[
            {
                "code": 405,
                "message": "Bad Alert ID"
            }
        ]
    )
    def patch(self, alert_id):
        """ Get a specific alert
        """
        if alert_id not in ALERTS:
            abort(404, alert_id=alert_id)
        return ALERTS[alert_id]



if __name__ == '__main__':
    blueprint = Blueprint('my_app', __name__)
    blueprint.add_url_rule('/alerts', view_func=AlertsEndpoint.as_view('alerts'))
    blueprint.add_url_rule('/alerts/<int:alert_id>', view_func=AlertEndpoint.as_view('alert'))

    app = Flask(__name__)
    api = Api(default_mediatype='application/json')
    # do not register the blueprint with flast.ext.restless.Api()
    # until after swagger has registered itself with the
    # blueprint with api.init_app(blueprint)

    # setup swagger docs using the blueprint.record callback
    api = swagger.docs(api, blueprint=blueprint)

    # register any restless resources you
    # may want here if required

    # now load blueprint into restless api
    api.init_app(blueprint)

    # then register blueprint
    app.register_blueprint(blueprint)

    app.run(debug=True)
