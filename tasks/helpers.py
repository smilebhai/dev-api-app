from requests import get
from requests.exceptions import HTTPError

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)  # Get logger by name


def api_request(url, params=None):
    """
    Return status of a ping command

    Args:
        host: in the form of either an IP address or Domain name

    Returns:
        Boolean. Evaulation of exit code
    """
    logger.info('START API REQUEST')
    try:
        response = get(url, params=params, timeout=60)
        # If successful, no Exception will be raised
        response.raise_for_status()
        logger.info('END API REQUEST')
        return response.json()
    except HTTPError as http_err:
        logger.info('HTTP error occurred: {}'.format(http_err))
        return {'status': 'ERROR', 'desc': str(http_err)}
    except Exception as err:
        logger.info('Other error occurred: {}'.format(err))
        return {'status': 'ERROR', 'desc': str(err)}
