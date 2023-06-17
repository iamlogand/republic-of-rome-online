from django.conf import settings
from debug_toolbar.middleware import DebugToolbarMiddleware

class InternalIPsDebugToolbarMiddleware(DebugToolbarMiddleware):
    def show_toolbar(self, request):
        return settings.DEBUG
