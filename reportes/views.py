from django.http import JsonResponse
from django.core.cache import cache
from django.db.models import Sum, Avg, Max
from .models import ConsumoMensual, Usuario
from .middleware import require_auth  
import time
from .alertas import verificar_y_alertar_sobrecosto   # ← nuevo import


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