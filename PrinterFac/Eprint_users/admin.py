from django.contrib import admin
from . models import Profile, CustSearch, HostSearch

# Register your models here.
admin.site.register(HostSearch)
admin.site.register(CustSearch)
admin.site.register(Profile)
