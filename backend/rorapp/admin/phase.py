from django.contrib import admin
from rorapp.models import Phase


# Admin configuration for phases
@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name", "index", "turn")
