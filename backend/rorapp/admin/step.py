from django.contrib import admin
from rorapp.models import Step


# Admin configuration for steps
@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ("__str__", 'index', 'phase')
