from django.core.management.base import BaseCommand
from reportes.models import Proyecto, ConsumoMensual
from reportes.alertas import verificar_y_alertar_sobrecosto

class Command(BaseCommand):
    help = 'Verifica sobrecostos en todos los proyectos y alerta si hay anomalías'

    def handle(self, *args, **kwargs):
        proyectos = Proyecto.objects.all()
        for proyecto in proyectos:
            consumos = ConsumoMensual.objects.filter(proyecto=proyecto)
            self.stdout.write(f'Verificando {proyecto.nombre}...')
            verificar_y_alertar_sobrecosto(proyecto, consumos)
        self.stdout.write(self.style.SUCCESS('Verificación completada.'))