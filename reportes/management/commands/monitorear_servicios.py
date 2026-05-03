import socket
import time
import logging
from django.core.management.base import BaseCommand
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

SERVICIOS = [
    {"nombre": "PostgreSQL (authd-db)",  "host": "172.31.37.110", "puerto": 5432},
    {"nombre": "Redis (nosqld-django)",  "host": "172.31.37.44",  "puerto": 6379},
    {"nombre": "MongoDB (nosqld-mongo)", "host": "172.31.47.158", "puerto": 27017},
]

DESTINATARIOS = ['santiqu192@gmail.com'] #TODO CAMBIAR
ESTADO_FILE = '/home/ubuntu/miau/estado_servicios.json'


def verificar_puerto(host, puerto, timeout=3):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        resultado = sock.connect_ex((host, puerto))
        sock.close()
        return resultado == 0
    except Exception:
        return False


def leer_estado():
    import json
    try:
        with open(ESTADO_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def guardar_estado(estado):
    import json
    try:
        with open(ESTADO_FILE, 'w') as f:
            json.dump(estado, f)
    except Exception as e:
        logger.error(f"Error guardando estado: {e}")


def notificar(asunto, cuerpo):
    try:
        send_mail(
            subject=asunto,
            message='',
            from_email='santiqu192@gmail.com', #TODO CAMBIAR
            recipient_list=DESTINATARIOS,
            html_message=cuerpo,
            fail_silently=False,
        )
        logger.info(f"[MONITOR] Email enviado: {asunto}")
    except Exception as e:
        logger.error(f"[MONITOR] Error enviando email: {e}")


class Command(BaseCommand):
    help = 'Monitorea servicios y notifica fallas y recuperaciones'

    def handle(self, *args, **kwargs):
        servidor  = socket.gethostname()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        estado    = leer_estado()

        for servicio in SERVICIOS:
            nombre = servicio["nombre"]
            host   = servicio["host"]
            puerto = servicio["puerto"]
            clave  = f"{host}:{puerto}"
            activo = verificar_puerto(host, puerto)

            estaba_caido = estado.get(clave, {}).get("caido", False)

            if not activo:
                if not estaba_caido:
                    # Primera vez que detecta la falla
                    estado[clave] = {"caido": True, "desde": timestamp, "reportado_por": servidor}
                    guardar_estado(estado)
                    self.stdout.write(f"[FALLA] {nombre} — notificando...")
                    notificar(
                        asunto=f"FALLA DETECTADA: {nombre}",
                        cuerpo=f"""
                        <h2>Alerta de disponibilidad — FinOps</h2>
                        <p>Se ha detectado una falla en el siguiente servicio:</p>
                        <ul>
                            <li>Servicio: <strong>{nombre}</strong></li>
                            <li>Host: <strong>{host}:{puerto}</strong></li>
                            <li>Detectado por: <strong>{servidor}</strong></li>
                            <li>Timestamp: <strong>{timestamp}</strong></li>
                        </ul>
                        <p>El equipo tecnico debe revisar el servicio.</p>
                        """
                    )
                else:
                    self.stdout.write(f"[FALLA] {nombre} — ya reportado, sigue caido")
            else:
                if estaba_caido:
                    caido_desde = estado[clave].get("desde", "desconocido")
                    del estado[clave]
                    guardar_estado(estado)
                    self.stdout.write(f"[RECUPERADO] {nombre} — notificando...")
                    notificar(
                        asunto=f"SERVICIO RECUPERADO: {nombre}",
                        cuerpo=f"""
                        <h2>Recuperacion de servicio — FinOps</h2>
                        <p>El siguiente servicio se ha recuperado correctamente:</p>
                        <ul>
                            <li>Servicio: <strong>{nombre}</strong></li>
                            <li>Host: <strong>{host}:{puerto}</strong></li>
                            <li>Caido desde: <strong>{caido_desde}</strong></li>
                            <li>Recuperado: <strong>{timestamp}</strong></li>
                            <li>Detectado por: <strong>{servidor}</strong></li>
                        </ul>
                        <p>El servicio esta operativo nuevamente.</p>
                        """
                    )
                else:
                    self.stdout.write(f"[OK] {nombre}")