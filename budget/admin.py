from django.contrib import admin
from .models import ConstantBudget, ScheduledBudget, SpecifiedBudget

class ConstantBudgetAdmin(admin.ModelAdmin):
	list_display = ('category','categorygroup','amount')

class ScheduledBudgetAdmin(admin.ModelAdmin):
	list_display = ('category','categorygroup','amount', 'last_date')

class SpecifiedBudgetAdmin(admin.ModelAdmin):
	list_display = ('category','categorygroup','amount', 'date')

admin.site.register(ConstantBudget, ConstantBudgetAdmin)
admin.site.register(ScheduledBudget, ScheduledBudgetAdmin)
admin.site.register(SpecifiedBudget, SpecifiedBudgetAdmin)
