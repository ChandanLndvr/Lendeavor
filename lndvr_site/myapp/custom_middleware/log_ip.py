import logging
import socket

logger = logging.getLogger('django_actions')

class LogClientIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            # Get hostname safely
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
        except Exception:
            hostname = 'Unknown'

        logger.info(f"Request from IP: {ip}, Hostname: {hostname}, Method: {request.method}, Path: {request.path}")
        response = self.get_response(request)
        return response