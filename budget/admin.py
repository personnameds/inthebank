from django.contrib import admin
from .models import ConstantBudget, ScheduledBudget

class ConstantBudgetAdmin(admin.ModelAdmin):
	list_display = ('category','categorygroup','amount')

class ScheduledBudgetAdmin(admin.ModelAdmin):
	list_display = ('category','categorygroup','amount', 'last_date')

admin.site.register(ConstantBudget, ConstantBudgetAdmin)
admin.site.register(ScheduledBudget, ScheduledBudgetAdmin)