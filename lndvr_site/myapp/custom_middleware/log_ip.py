import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler as RotatingFileHandler
from datetime import datetime
import pytz

# --- Custom Formatter that logs in US Eastern Time (handles EDT/EST) ---
class ESTFormatter(logging.Formatter):
    def converter(self, timestamp):
        dt_utc = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
        return dt_utc.astimezone(pytz.timezone("US/Eastern"))

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()

# === Logger Setup ===
logger = logging.getLogger('django_actions')
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    'django_actions.log',
    maxBytes=10 * 1024 * 1024,
    backupCount=5
)

# Use ESTFormatter to log in Eastern Time
formatter = ESTFormatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p %Z')
handler.setFormatter(formatter)

logger.addHandler(handler)

# === Utility Functions ===

def get_client_ip(request):
    """
    Extract the client IP address from the Django request object.
    Checks 'HTTP_X_FORWARDED_FOR' for proxy scenarios; falls back to 'REMOTE_ADDR'.
    """
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_action(request, action_desc, user_info=None):
    """
    Logs an action with timestamp, method, description, IP, and user info.

    Args:
    - request: Django request object.
    - action_desc (str): Description of the action.
    - user_info (str): Optional user identifier (email, username).
    """
    ip = get_client_ip(request)
    method = request.method
    user = user_info or (request.user if hasattr(request, 'user') else 'Anonymous')
    logger.info(f"Method: {method} | Action: {action_desc} | IP: {ip} | User: {user}") # follows this format %(asctime)s - %(levelname)s - %(message)s
    # sample output for above logger.info -> 2025-07-22 14:35:01,123 - INFO - Method: POST | Action: Signup attempt | IP: 123.45.67.89 | User: Anonymous


"""Below method will provide u the log of all the action taking place on site, 
    but this will increase the size of the log file. we are commenting out this method and will create log only for sensitive methods or actions"""
    # def __call__(self, request):
    #     ip = request.META.get('HTTP_X_FORWARDED_FOR')
    #     if ip:
    #         ip = ip.split(',')[0]
    #     else:
    #         ip = request.META.get('REMOTE_ADDR')
    #         # Get hostname safely
    #     try:
    #         hostname, _, _ = socket.gethostbyaddr(ip)
    #     except Exception:
    #         hostname = 'Unknown'

    #     # logger.info(f"Request from IP: {ip}, Hostname: {hostname}, Method: {request.method}, Path: {request.path}") # this will get u the logs of all the actions taking palce on your site
    #     response = self.get_response(request)
    #     return response