from flask_restx import Resource, Namespace
from datetime import datetime

# Set namespace
ns = Namespace('ratelimit', description='Ratelimit operations',
               ordered=True)

log = ns.logger


# Define default route resources
@ns.route('/test', endpoint="/test")
class Test(Resource):
    def get(self):
        '''Execute multiple times until you hit the default rate limits per minute.'''

        """
        A test method to test the default rate limits

        Returns:
            JSON - current time
        """

        log.info("START {}".format(self.endpoint))

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        log.info("END {}".format(self.endpoint))
        return {'time': current_time}
