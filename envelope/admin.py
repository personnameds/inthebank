from django.contrib import admin
from .models import Envelope

class EnvelopeAdmin(admin.ModelAdmin):
	list_display = ('category','categorygroup','amount','date')

admin.site.register(Envelope, EnvelopeAdmin)