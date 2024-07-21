from django.contrib import admin
from rorapp.models import Concession


# Admin configuration for concessions
@admin.register(Concession)
class ConcessionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "name", "game", "senator")
