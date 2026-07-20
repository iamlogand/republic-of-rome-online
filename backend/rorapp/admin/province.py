from django.contrib import admin

from rorapp.models import Province


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ("__str__", "game", "name", "developed")
