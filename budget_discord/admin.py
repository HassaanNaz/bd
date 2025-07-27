from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(User)
admin.site.register(Friend_Request)
admin.site.register(Friend)
admin.site.register(Group)
admin.site.register(Group_Member)
admin.site.register(DM_Message)
admin.site.register(Group_Message)