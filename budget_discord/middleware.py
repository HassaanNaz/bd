from .models import User
from datetime import datetime

class ActiveUserMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            user.last_seen = datetime.now()
            user.save()

