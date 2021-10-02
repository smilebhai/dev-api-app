from flask_restx import Namespace, Resource
from celery import states
from backend import tasks_app
from routes.helpers import task_error

# Set namespace
ns = Namespace('tasks', description='Task Queue Job operations', ordered=True)

log = ns.logger


# Define route resources
@ns.route('/status/<string:task_id>', endpoint="/status/task_id")
@ns.param('task_id', 'Task Job ID')
@ns.response(500, 'Job error')
class GetTaskStatus(Resource):

    @ns.response(303, 'Task successfully finished')
    @ns.response(200, 'Task unknown or not yet started')
    def get(self, task_id):
        '''Returns the status of a task job'''

        """
        Fetch the status of the task job

        :param task_id: celery worker task id

        Returns:
            JSON - Return task id along with the task job status OR
            error information
        """
        response = {}

        ns.logger.info("START {}".format(self.endpoint))

        result = tasks_app.AsyncResult(task_id, app=tasks_app)
        state = result.state

        # the task has been started
        if state == states.STARTED:
            response = {'task_id': result.id, 'status': state}, 200

        # the task is waiting for execution
        elif state == states.PENDING:
            response = {'task_id': result.id, 'status': state}, 200

        # the task executed successfully
        # the result attribute then contains the tasks return value
        elif state == states.SUCCESS:
            response = {'task_id': result.id, 'status': state}

        else:
            response = task_error(result)

        ns.logger.info("END {}".format(self.endpoint))

        return response


# Define route resources
@ns.route('/result/<task_id>', endpoint="/result/task_id/")
@ns.param('task_id', 'Task Job ID')
@ns.response(500, 'Job error')
class GetTaskResult(Resource):

    @ns.response(404, 'Result do not exists')
    @ns.response(200, 'Return result')
    def get(self, task_id):
        '''Returns the result of a task job'''

        """
        Fetch the result of the task job

        :param task_id: celery worker task id

        Returns:
            JSON - Return task id along with the task job results
            OR error information
        """
        response = {}

        ns.logger.info("START {}".format(self.endpoint))
        result = tasks_app.AsyncResult(task_id, app=tasks_app)

        state = result.state

        # tasks finished so result exists
        if state == states.SUCCESS:
            response = {'task_id': result.id, 'status': state,
                        'result': result.get(timeout=1.0)}, 200

        # task still pending or unknown - so result do not exists
        elif state == states.PENDING:
            response = {'task_id': result.id, 'status': state}, 404

        # task started but result do not exists yet
        elif state == states.STARTED:
            response = {'task_id': result.id, 'status': state}, 404

        else:
            response = task_error(result)

        ns.logger.info("END {}".format(self.endpoint))

        return response
