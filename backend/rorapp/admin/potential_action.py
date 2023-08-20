from django.contrib import admin
from rorapp.models import PotentialAction


# Admin configuration for potential actions
@admin.register(PotentialAction)
class PotentialActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'step', 'type')
    
    # String representation of the potential action, used in admin site
    def __str__(self):
        return f'{self.name} of {self.turn.index}'
