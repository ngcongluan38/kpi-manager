from django.apps import AppConfig


class KpiManagerConfig(AppConfig):
    name = 'kpi_manager'

    def ready(self):
        import kpi_manager.signals
