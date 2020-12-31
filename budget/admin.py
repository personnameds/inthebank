from django.contrib import admin
from .models import ConstantBudget, ScheduledBudget, SpecificBudget

class ConstantBudgetAdmin(admin.ModelAdmin):
	list_display = ('category','categorygroup','amount')

class ScheduledBudgetAdmin(admin.ModelAdmin):
	list_display = ('category','categorygroup','amount', 'last_date')

class SpecificBudgetAdmin(admin.ModelAdmin):
	list_display = ('category','categorygroup','amount', 'budget_month')

admin.site.register(ConstantBudget, ConstantBudgetAdmin)
admin.site.register(ScheduledBudget, ScheduledBudgetAdmin)
admin.site.register(SpecificBudget, SpecificBudgetAdmin)