from django.contrib import admin

from .models import Category
from .models import CategoryGroup

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('group','name',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryGroup)