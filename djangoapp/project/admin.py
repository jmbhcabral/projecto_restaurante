from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User


class UserAdmin(DefaultUserAdmin):

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return list(self.readonly_fields) + ['username']
        return self.readonly_fields


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
