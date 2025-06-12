import jwt
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Configuration
SECRET_KEY = settings.SECRET_KEY
JWT_EXPIRATION_DELTA = timedelta(days=1)  # Token expires in 1 day

# Password utilities
def hash_password(raw_password):
    return make_password(raw_password)

def verify_password(raw_password, hashed_password):
    return check_password(raw_password, hashed_password)

# JWT utilities
def generate_jwt(payload):
    """
    Generates a JWT token with expiration using Django's timezone utilities.
    """
    expiration = timezone.now() + JWT_EXPIRATION_DELTA
    payload['exp'] = int(expiration.timestamp())  # JWT requires a UNIX timestamp
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def decode_jwt(token):
    """
    Decodes a JWT token and returns the payload, or None if invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
    
# Password reset token generator
class SignUpTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.Email}{user.Password}"

token_generator = SignUpTokenGenerator()
