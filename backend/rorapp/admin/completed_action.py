from django.contrib import admin
from rorapp.models import CompletedAction


# Admin configuration for completed actions
@admin.register(CompletedAction)
class CompletedActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'step', 'type')
    
    # String representation of the completed action, used in admin site
    def __str__(self):
        return f'{self.name} of {self.turn.index}'
