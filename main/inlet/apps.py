from django.apps import AppConfig


class InletConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inlet'


def ready(self):
    print("IMPORTED")
    import inlet.signals 