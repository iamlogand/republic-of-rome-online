from django.contrib import admin
from rorapp.models import Secret


# Admin configuration for secrets
@admin.register(Secret)
class SecretAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name", "type", "faction")
