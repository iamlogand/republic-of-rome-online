from django.contrib import admin
from rorapp.models import Office


# Admin configuration for offices
@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', "senator", "start_step", "end_step")
