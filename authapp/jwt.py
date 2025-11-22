import jwt, datetime
from django.conf import settings

def create_jwt(farmer_id):
    payload = {
        "farmer_id": farmer_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
