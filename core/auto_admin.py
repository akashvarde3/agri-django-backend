from django.contrib import admin
from django.apps import apps

def autoregister():
    for app_config in apps.get_app_configs():
        for model_name, model in app_config.models.items():
            try:
                admin.site.register(model)
            except admin.sites.AlreadyRegistered:
                pass  # ignore if already registered