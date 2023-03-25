from django.contrib import admin
from .models import Category, CategoryGroup

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('group','name', 'budget_method','remainder')


class CategoryGroupAdmin(admin.ModelAdmin):
	list_display = ('name', 'budget_method','remainder')


admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryGroup, CategoryGroupAdmin)