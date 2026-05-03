from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db.models import Sum, Avg, Max
from reportes.models import Proyecto, ConsumoMensual
import time

class Command(BaseCommand):
    help = 'Envía reporte diario de costos a todos los proyectos'

    def handle(self, *args, **kwargs):
        proyectos = Proyecto.objects.all()
        cuerpo = f"<h2>Reporte Diario FinOps — {time.strftime('%Y-%m-%d')}</h2>"

        for proyecto in proyectos:
            consumos = ConsumoMensual.objects.filter(proyecto=proyecto)
            total   = consumos.aggregate(Sum('costo_total'))['costo_total__sum'] or 0
            promedio = consumos.aggregate(Avg('costo_total'))['costo_total__avg'] or 0
            maximo  = consumos.aggregate(Max('costo_total'))['costo_total__max'] or 0

            cuerpo += f"""
            <h3>{proyecto.nombre}</h3>
            <ul>
                <li>Costo total acumulado: <strong>${total:,.2f} USD</strong></li>
                <li>Costo promedio mensual: <strong>${promedio:,.2f} USD</strong></li>
                <li>Costo máximo registrado: <strong>${maximo:,.2f} USD</strong></li>
            </ul>
            """

        destinatarios = ['santiqu192@gmail.com']
        send_mail(
            subject=f'Reporte Diario FinOps — {time.strftime("%Y-%m-%d")}',
            message='',
            from_email='santiqu192@gmail.com', #TODO CAMBIAR
            recipient_list=destinatarios,
            html_message=cuerpo,
            fail_silently=False,
        )
        self.stdout.write(self.style.SUCCESS('Reporte diario enviado.'))