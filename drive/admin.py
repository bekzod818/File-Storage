from django.contrib import admin

from .models import File, Group, Permission, Sharing

admin.site.register(File)
admin.site.register(Group)
admin.site.register(Permission)
admin.site.register(Sharing)
