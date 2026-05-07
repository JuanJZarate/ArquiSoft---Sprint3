from django.http import JsonResponse
from django.core.cache import cache
from django.db.models import Sum, Avg, Max
from .models import ConsumoMensual, Usuario
from .middleware import require_auth  
import time
from .alertas import verificar_y_alertar_sobrecosto   # ← nuevo import
from .alertas import enviar_email_con_reintento

@require_auth('financial-team', 'project-leader') 
def generar_reporte_finops(request, usuario_id, proyecto_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado."}, status=404)

    if not usuario.proyecto or usuario.proyecto.id != proyecto_id:
        return JsonResponse({"error": "El usuario no pertenece a este proyecto."}, status=403)

    proyecto = usuario.proyecto

    cache_key = f'reporte_proyecto_{proyecto_id}'
    reporte = cache.get(cache_key)

    if not reporte:
        time.sleep(1)  # Simula proceso pesado

        consumos = ConsumoMensual.objects.filter(proyecto=proyecto)
        reporte = {
            "metrica": "ASR 1.1 - Alto Rendimiento",
            "status": "Calculado y Guardado en Redis",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "proyecto": proyecto.nombre,
            "costo_total": float(consumos.aggregate(Sum('costo_total'))['costo_total__sum'] or 0),
            "costo_promedio": float(consumos.aggregate(Avg('costo_total'))['costo_total__avg'] or 0),
            "costo_maximo": float(consumos.aggregate(Max('costo_total'))['costo_total__max'] or 0),
        }
        verificar_y_alertar_sobrecosto(proyecto, consumos)
        cache.set(cache_key, reporte, timeout=600)
        print("DEBUG: Reporte calculado desde cero.")
    else:
        print("DEBUG: Reporte servido desde REDIS (Instantáneo).")

    return JsonResponse(reporte)


@require_auth('technical-team', 'project-leader')
def monitoreo_infra(request, usuario_id, proyecto_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado."}, status=404)

    if not usuario.proyecto or usuario.proyecto.id != proyecto_id:
        return JsonResponse({"error": "El usuario no pertenece a este proyecto."}, status=403)

    proyecto = usuario.proyecto
    consumos = ConsumoMensual.objects.filter(proyecto=proyecto)

    return JsonResponse({
        "metrica": "ASR - Monitoreo Infraestructura",
        "proyecto": proyecto.nombre,
        "total_registros": consumos.count(),
        "ultimo_mes": consumos.order_by('-anio', '-mes').values('mes', 'anio', 'costo_total').first(),
    })
    

@require_auth('technical-team', 'project-leader')
def monitoreo_infra(request, usuario_id, proyecto_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado."}, status=404)

    if not usuario.proyecto or usuario.proyecto.id != proyecto_id:
        return JsonResponse({"error": "El usuario no pertenece a este proyecto."}, status=403)

    proyecto = usuario.proyecto

    # Verificar integridad de los registros
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.consumo_id, a.valor_original, a.valor_alterado, a.detectado_en
            FROM reportes_alerta_integridad a
            WHERE a.revertido = TRUE
            AND a.detectado_en > NOW() - INTERVAL '1 hour'
            ORDER BY a.detectado_en DESC
        """)
        alertas = cursor.fetchall()

    if alertas:
        cuerpo = f"""
        <h2>Alerta de Integridad — FinOps</h2>
        <p>Se detectaron alteraciones en el proyecto <strong>{proyecto.nombre}</strong>:</p>
        <ul>
        """
        for alerta in alertas:
            cuerpo += f"""
            <li>Registro #{alerta[0]}: valor alterado de 
                <strong>${alerta[1]}</strong> a 
                <strong>${alerta[2]}</strong> — 
                detectado y revertido a las {alerta[3]}
            </li>
            """
        cuerpo += "</ul><p>Todos los cambios fueron revertidos automaticamente.</p>"

        destinatarios = list(proyecto.usuarios.values_list('email', flat=True))
        enviar_email_con_reintento(
            destinatarios=destinatarios,
            asunto=f"ALERTA INTEGRIDAD: {proyecto.nombre}",
            cuerpo_html=cuerpo
        )

    consumos = ConsumoMensual.objects.filter(proyecto=proyecto)

    return JsonResponse({
        "metrica": "ASR Integridad - Monitoreo Infraestructura",
        "proyecto": proyecto.nombre,
        "total_registros": consumos.count(),
        "ultimo_mes": list(consumos.order_by('-anio', '-mes').values('mes', 'anio', 'costo_total')[:1]),
        "alertas_integridad_ultima_hora": len(alertas),
        "estado": "INTEGRIDAD OK" if not alertas else "ALTERACIONES DETECTADAS Y REVERTIDAS"
    })