from django.urls import path, register_converter
from category.views import SpendingView, SpendingFilterFormView, SpendingFilterView
from category.views import CategoryGroupUpdateView, CategoryGroupCreateView, CategoryGroupDeleteView
from category.views import CategoryListView, CategoryUpdateView, CategoryDeleteView, CategoryCreateView
from datetime import datetime


class DateConverter:
	regex = '\d{4}-\d{2}-\d{2}'

	def to_python(self, value):
		return datetime.strptime(value, '%Y-%m-%d')
	
	def to_url(self, value):
		return value

register_converter(DateConverter, 'yyyy')

urlpatterns = [
    path('', CategoryListView.as_view(), name='category-list'),
    path('update/group/<int:pk>/', CategoryGroupUpdateView.as_view(), name='category-group-update'),
    path('delete/group/<int:pk>/', CategoryGroupDeleteView.as_view(), name='category-group-delete'),
    path('create/group/', CategoryGroupCreateView.as_view(), name='category-group-create'),
    path('update/cat/<int:pk>/', CategoryUpdateView.as_view(), name='category-update'),
    path('create/cat/<int:group_pk>/', CategoryCreateView.as_view(), name='category-create'),
    path('delete/cat/<int:pk>/', CategoryDeleteView.as_view(), name='category-delete'),
    path('spending/', SpendingView.as_view(), name='spending-list'),
    path('spending/<int:year>/<int:month>/', SpendingView.as_view(), name='spending-list'),
    path('spending/filter/<yyyy:from_date>/<yyyy:to_date>/<int:group>/', SpendingFilterView.as_view(), name='spending-filter-list'),
    path('spending/filter/', SpendingFilterFormView.as_view(), name='spending-filter'),
]
