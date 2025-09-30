from django.contrib import admin
from .models import Users, Address, Specialty, Doctor, Administrator, Receptions, Reset_token

# Register your models here.

admin.site.register(Users)
admin.site.register(Address)
admin.site.register(Specialty)
admin.site.register(Doctor)
admin.site.register(Receptions)
admin.site.register(Administrator)
admin.site.register(Reset_token)


