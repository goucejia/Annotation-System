from django.contrib import admin

# Register your models here.

from user import models
admin.site.register(models.UserProfile)

admin.site.register(models.File)
admin.site.register(models.FileShare)

admin.site.register(models.Group)
admin.site.register(models.GroupMember)
admin.site.register(models.GroupFiles)

admin.site.register(models.Label)