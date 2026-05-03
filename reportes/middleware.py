import json
import logging
from functools import wraps
from django.http import JsonResponse
from .auth0 import validate_token, get_token_from_request, get_roles_from_payload

audit_logger = logging.getLogger('audit')


def log_audit(user_id, roles, resource, result, ip):
    audit_logger.info(json.dumps({
        'type':      'AUDIT',
        'userId':    user_id,
        'roles':     roles,
        'resource':  resource,
        'result':    result,  # 'GRANTED' o 'DENIED'
        'ip':        ip,
    }))


def require_auth(*allowed_roles):
    """
    Decorador que valida JWT y verifica que el usuario
    tenga al menos uno de los roles permitidos.
    Uso: @require_auth('financial-team', 'project-leader')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            token = get_token_from_request(request)

            if not token:
                return JsonResponse(
                    {'error': 'Token no proporcionado.'}, status=401
                )

            try:
                payload = validate_token(token)
            except Exception as e:
                return JsonResponse(
                    {'error': f'Token inválido: {str(e)}'}, status=401
                )

            user_id  = payload.get('sub', 'unknown')
            roles    = get_roles_from_payload(payload)
            resource = request.path
            ip       = request.META.get('REMOTE_ADDR', '')

            has_access = any(r in roles for r in allowed_roles)

            log_audit(
                user_id=user_id,
                roles=roles,
                resource=resource,
                result='GRANTED' if has_access else 'DENIED',
                ip=ip,
            )

            if not has_access:
                return JsonResponse(
                    {'error': 'No tienes permisos para acceder a este recurso.'},
                    status=403
                )

            # Inyectar info del usuario en el request para uso en la vista
            request.auth_user_id = user_id
            request.auth_roles   = roles
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator