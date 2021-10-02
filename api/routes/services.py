from backend import tasks_app
from flask_restx import Resource, fields, Namespace
from routes.helpers import token_required
from validators import ipv4, domain
from settings import SERVICES, PING, RDAP, IP, DOMAIN, \
    SAMPLE_DOMAIN, SAMPLE_APIKEY


# Set namespace
ns = Namespace('services', description='Service operations', ordered=True)

log = ns.logger

# Register models
service_json = fields.List(fields.String(required=False, example='ping'))
service_model = ns.model('Service arguments', {'services': service_json})

virustotal_model = ns.model('Virustotal arguments', {
    'apikey': fields.String(required=True,
                            description='Your API key',
                            example=SAMPLE_APIKEY),
    'domain_name': fields.String(required=True,
                                 description='A Domain name',
                                 example=SAMPLE_DOMAIN)
})


def service_available(service):
    """
    Check if a user provided service is available to process

    :param service: name of the the service

    Returns:
        Boolean evaulation.
    """

    for svc in SERVICES:
        if service.lower() == svc.lower():
            return True

    return False


def do_service(host, list_of_services, host_type):
    """
    Gathers information from multiple sources.
    Process each service lookup on different Celery
    task workers to perform the action.

    :param host: ip or domain name
    :param list_of_services: a list of sevices to lookup
    :param host_type: 'IP' or 'DOMAIN'

    Returns:
        JSON - Combine the results and return a single payload
    """

    task_ids = []
    response = []

    # Process each service and add to a task queue
    for service in list_of_services:
        if service_available(service):

            ns.logger.info("START {}".format(service))

            if service.upper() == PING:

                """
                Process ping service
                """

                try:
                    result = tasks_app.send_task('tasks.ping',
                                                 kwargs={'host': host})

                    ns.logger.info(result.backend)
                    ns.logger.info("{} results: {}".format(
                        service, result.state))

                    task_ids.append({'service': service, 'task_id': result.id})

                except Exception:
                    ns.logger.info("Error with {} on {}".format(service, host))
                    response.append({
                        'host': host,
                        'service': service,
                        'results': 'error'
                    })

            elif service.upper() == RDAP:

                """
                Process rdap service
                """

                try:

                    result = tasks_app.send_task('tasks.rdap',
                                                 args=(host, host_type))

                    ns.logger.info(result.backend)
                    ns.logger.info("{} results: {}".format(
                        service,
                        result.state))

                    task_ids.append({'service': service,
                                     'task_id': result.id})
                except Exception:
                    ns.logger.info("Error with {} on {}".format(
                        service,
                        host))
                    response.append({
                        'host': host,
                        'service': service,
                        'results': 'error'
                    })

        else:
            ns.logger.info("Error with {} on {}".format(service, host))
            response.append({
                'host': host,
                'service': service,
                'results': 'invalid service'
            })

    # Combine the resullt of each task in the task queue
    # and generate a single payload
    for task in task_ids:
        id = task['task_id']
        service = task['service']
        result = tasks_app.AsyncResult(id, app=tasks_app)

        ns.logger.info("Process task: {}".format(id))
        try:
            # Wait 60 seconds, before the operation times out
            result_output = result.wait(timeout=60, interval=0.5)
            response.append({
                'task_id': id,
                'host': host,
                'service': service,
                'results': result_output
            })

        except Exception as e:
            ns.logger.info("Celery task didn't complete: Celery may be down.")
            response.append({
                'task_id': id,
                'host': host,
                'service': service,
                'results': str(e)
            })

    return response


# Define route resources
@ns.route('/default/<host>', endpoint="host")
class LookupService(Resource):

    # specify one of the expected responses and parameters
    @ns.doc(responses={
            200: 'OK',
            400: 'Invalid Argument',
            500: 'Mapping Key Error'
            },
            params={
            'host': {
                'description': 'Specify an IP address or Domain name',
                'default': '8.8.8.8'
            }
            })
    # Specify the expected input model
    @ns.expect(service_model, validate=False)
    @ns.doc(security='apikey')
    @token_required
    def post(self, host):
        '''Returns information from selected services.
        Leave blank for all available services
        ***TOKEN AUTHORIZATION REQUIRED***'''

        """
        Schedule a separate Celery task job for each service
        from a list of provided services.

        :param host: ip or domain name
        :param services: list of services to query or use default list if none provided

        Returns:
            JSON - Combine the results and return a single payload
        """

        ns.logger.info("START {}".format(self.endpoint))
        # Validate IP or Domain
        host_type = ''
        response = {}

        if ipv4(host):
            host_type = IP
        elif domain(host):
            host_type = DOMAIN
        else:
            return {'results':
                    'invalid host: enter correct ip address or domain name'}

        if ns.payload:
            if 'services' in ns.payload:
                request_args = ns.payload
                list_of_services = request_args['services']

                if list_of_services:
                    response = do_service(host, list_of_services, host_type)
                else:
                    response = do_service(host, SERVICES, host_type)

            else:
                response = do_service(host, SERVICES, host_type)
        else:
            response = do_service(host, SERVICES, host_type)

        return {'services': response}


# Define route resources
@ns.route('/virustotal/domain/report', endpoint="/virustotal/domain/report")
class AddVirusTotalJob(Resource):

    # specify one of the expected responses and parameters
    @ns.doc(responses={
            200: 'OK',
            400: 'Invalid Argument',
            500: 'Mapping Key Error'
            })
    # Specify the expected input model
    @ns.expect(virustotal_model, validate=True)
    def post(self):
        '''Schedules a VirusTotal Domain Report task job'''

        """
        Fetch data from VirusTotal /domain/report endpoint

        :param apikey: API Key to authenticate with VirusTotal API Service
        :param domain_name: domain name on which to process the request

        Returns:
            JSON - Return task id of the job and
            initial status OR error information
        """
        response = {}

        ns.logger.info("START {}".format(self.endpoint))

        domain_name = ns.payload['domain_name']
        apikey = ns.payload['apikey']

        if domain_name and apikey:
            if domain(domain_name):
                ns.logger.info("EXECUTE {}".format(self.endpoint))
                result = tasks_app.send_task('tasks.virustotal_domain_report',
                                             args=(apikey, domain_name))

                ns.logger.info(result.backend)

                response = {'task_id': result.id, 'status': result.state}
            else:
                response = {'ERROR': 'Not a valid Domain name'}
        else:
            response = {'ERROR': 'Empty values are not allowed'}

        ns.logger.info("END {}".format(self.endpoint))

        return response
