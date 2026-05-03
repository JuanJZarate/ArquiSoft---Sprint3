import time
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings

logger = logging.getLogger(__name__)

UMBRAL_SOBRECOSTO = 100000 # USD — ajustalo según el proyecto


def enviar_email_con_reintento(destinatarios, asunto, cuerpo_html,
                                max_intentos=3, espera_base=2):
    """
    Envía email con reintentos exponenciales.
    Lanza excepción solo si agota todos los intentos (va a DLQ o log crítico).
    """
    for intento in range(1, max_intentos + 1):
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = asunto
            msg['From']    = settings.EMAIL_HOST_USER
            msg['To']      = ', '.join(destinatarios)
            msg.attach(MIMEText(cuerpo_html, 'html'))

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.sendmail(settings.EMAIL_HOST_USER, destinatarios, msg.as_string())

            logger.info(f"[ALERTA OK] Email enviado a {destinatarios} (intento {intento})")
            return True

        except Exception as e:
            logger.warning(f"[ALERTA FALLO] Intento {intento}/{max_intentos}: {e}")
            if intento < max_intentos:
                time.sleep(espera_base ** intento)  # 2s, 4s, 8s

    # Agotó reintentos — registrar como crítico para intervención manual
    logger.critical(
        f"[ALERTA CRITICA] Email no entregado tras {max_intentos} intentos. "
        f"Destinatarios: {destinatarios}. Asunto: {asunto}"
    )
    return False


def verificar_y_alertar_sobrecosto(proyecto, consumos):
    """
    Llama a esta función desde la vista después de calcular el reporte.
    """
    from django.db.models import Max
    costo_max = consumos.aggregate(Max('costo_total'))['costo_total__max'] or 0

    if float(costo_max) <= UMBRAL_SOBRECOSTO:
        return  # Sin sobrecosto, no hacer nada

    # Obtener destinatarios: todos los usuarios del proyecto
    destinatarios = list(
        proyecto.usuarios.values_list('email', flat=True)
    )
    if not destinatarios:
        logger.warning(f"[ALERTA] Sobrecosto en {proyecto.nombre} pero sin destinatarios.")
        return

    asunto = f"Sobrecosto detectado en {proyecto.nombre}"
    cuerpo = f"""
    <h2>Alerta de Consumo Inusual — FinOps</h2>
    <p>Se ha detectado un sobrecosto en el proyecto <strong>{proyecto.nombre}</strong>.</p>
    <ul>
      <li>Costo máximo registrado: <strong>${costo_max:,.2f} USD</strong></li>
      <li>Umbral configurado: <strong>${UMBRAL_SOBRECOSTO:,.2f} USD</strong></li>
    </ul>
    <p>Revisa el dashboard para más detalles.</p>
    """

    enviar_email_con_reintento(destinatarios, asunto, cuerpo)