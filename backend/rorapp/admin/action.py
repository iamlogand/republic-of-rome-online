from django.contrib import admin
from rorapp.models import Action


# Admin configuration for actions
@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ("id", "step", "type", "completed")

    # String representation of the action, used in admin site
    def __str__(self):
        return f"{self.name} of {self.turn.index}"
