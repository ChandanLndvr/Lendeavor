import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler as RotatingFileHandler
#import socket

# Create a logger named 'django_actions'
logger = logging.getLogger('django_actions')

# Set the logging level to INFO to capture info, warnings, errors, and critical messages
logger.setLevel(logging.INFO)

# Set up a rotating file handler to manage log file size and backups
handler = RotatingFileHandler(
    'django_actions.log',      # Log file name
    maxBytes=10*1024*1024,      # Rotate log after it reaches 10 MB
    backupCount=5              # Keep last 5 rotated log files as backup
)

# Define the format of the log messages to include timestamp, log level, and the message
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the configured handler to the logger
logger.addHandler(handler)


def get_client_ip(request):
    """
    Extract the client IP address from the Django request object.
    Handles the case where the client is behind a proxy by
    checking 'HTTP_X_FORWARDED_FOR' header; otherwise uses 'REMOTE_ADDR'.
    Returns the first IP if multiple IPs are forwarded.
    """
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_action(request, action_desc, user_info=None):
    """
    Helper function to log an action with useful details.
    Logs include HTTP method, action description, client IP, and user info.
    
    Parameters:
    - request: Django HttpRequest object.
    - action_desc: A string describing the action being logged (e.g., "User signup").
    - user_info: Optional custom user identifier; defaults to request.user or 'Anonymous'.
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