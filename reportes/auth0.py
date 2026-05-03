import json
import urllib.request
from jose import jwt
from django.conf import settings
from django.http import JsonResponse
from functools import wraps


def get_jwks():
    url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())


def validate_token(token):
    jwks = get_jwks()
    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'], 'kid': key['kid'],
                'use': key['use'], 'n':   key['n'],
                'e':   key['e'],
            }

    return jwt.decode(
        token,
        rsa_key,
        algorithms=['RS256'],
        audience=settings.AUTH0_AUDIENCE,
        issuer=f"https://{settings.AUTH0_DOMAIN}/",
    )


def get_token_from_request(request):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header.split(' ')[1]


def get_roles_from_payload(payload):
    namespace = settings.AUTH0_NAMESPACE
    return payload.get(f'{namespace}/roles', [])