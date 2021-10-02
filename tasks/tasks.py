from celery import Celery
from celery.utils.log import get_task_logger
from os import environ, system
from time import sleep
from helpers import api_request
from settings import RDAP_DOMAIN_URL, RDAP_IP_URL, IP, DOMAIN, VIRUSTOTAL_DOMAIN_REPORT_URL

logger = get_task_logger(__name__)  # Get logger by name

# Initialize an instance of Celery

environ.setdefault('CELERY_CONFIG_MODULE', 'celery_config')

tasks_app = Celery('tasks')

tasks_app.config_from_envvar('CELERY_CONFIG_MODULE')


# Defined a Celery task to ping a host
@tasks_app.task()
def ping(host):
    """
    Return status of a ping command

    Args:
        host: in the form of either an IP address or Domain name

    Returns:
        Boolean. Evaulation of exit code
    """
    logger.info('START PING')

    parameter = "-c"

    exit_code = system("ping {} 3 {} > /dev/null 2>&1"
                          .format(parameter, host))

    logger.info('END PING')
    return {'success': exit_code == 0}


# Defined a Celery task to return rdap information for a given host (ip/domain)
@tasks_app.task()
def rdap(host, host_type):
    """
    Return response from rdap service endpoint

    Args:
        host: in the form of either an IP address or Domain name
        host_type: IP, DOMAIN

    Returns:
        JSON: Result of request
    """
    logger.info('START RDAP')

    domain_endpoint = RDAP_DOMAIN_URL
    ip_endpoint = RDAP_IP_URL

    if host_type == IP:
        url = ip_endpoint + host
    elif host_type == DOMAIN:
        url = domain_endpoint + host
    else:
        logger.info('END RDAP')
        return {'status': 'ERROR', 'desc': 'invalid host type'}

    response = api_request(url)
    logger.info('END RDAP')
    return response


# Defined a Celery task to return Virustotal information
# for the domain/report endpont
@tasks_app.task()
def virustotal_domain_report(apikey, domain):
    """
    Return response from VirusTotal domain report endpoint

    Args:
        apikey: API Key to access VirusTotal
        domain: A domain name

    Returns:
        JSON: Result of request
    """
    logger.info('START VIRUSTOTAL DOMAIN REPORT')

    url = VIRUSTOTAL_DOMAIN_REPORT_URL
    params = {'apikey': apikey, 'domain': domain}

    response = api_request(url, params)
    logger.info('END VIRUSTOTAL DOMAIN REPORT')

    return response

@tasks_app.task(queue='tests')
def add_numbers(x, y):
    return x + y