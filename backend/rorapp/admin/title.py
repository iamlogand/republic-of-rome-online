from django.contrib import admin
from rorapp.models import Title


# Admin configuration for titles
@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', "senator", "start_step", "end_step", 'major_office')
