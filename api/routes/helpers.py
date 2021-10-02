from flask import request
from functools import wraps
from settings import TOKEN


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        """
        Test user provided api token in the X-API-KEY key of the request.headers 
        with the stored env variable token value

        :param token: api token

        Returns:
            The function is token is correct otherwise a JSON message containing the error
        """
        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {'message': 'missing token'}, 401

        if token != TOKEN:
            return {'message': 'incorrect token'}, 401

        return f(*args, **kwargs)

    return decorated


def task_error(result):
    """
    Define a generic Celery task error

    :param result: result object of a task

    Returns:
        JSON. Error cause details
    """

    try:
        cause = 'task state : {} - '.format(result.state) + \
            result.info.get('error')

    except Exception:
        cause = 'task state : {} - '.format(result.state) + \
            'Unknown error occurred'

    return {'task_id': result.id, 'status': 'ERROR', 'desc': cause}, 500
