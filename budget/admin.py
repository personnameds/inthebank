from django.contrib import admin
from .models import ConstantBudget, AvgQuarterBudget

class ConstantBudgetAdmin(admin.ModelAdmin):
	list_display = ('category','categorygroup','amount','remainder')

class AvgQuarterBudgetAdmin(admin.ModelAdmin):
	list_display = ('category','categorygroup','remainder')

admin.site.register(ConstantBudget, ConstantBudgetAdmin)
admin.site.register(AvgQuarterBudget, AvgQuarterBudgetAdmin)