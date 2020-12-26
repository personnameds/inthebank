from django.urls import path
from .views import CategoryListView, SpendingView
from .views import CategoryGroupUpdateView, CategoryUpdateView

urlpatterns = [
    path('', CategoryListView.as_view(), name='category-list'),
    path('update/group/<int:pk>/', CategoryGroupUpdateView.as_view(), name='category-group-update'),
    path('update/cat/<int:pk>/', CategoryUpdateView.as_view(), name='category-update'),
    path('spending/', SpendingView.as_view(), name='spending-list'),
    path('spending/<int:year>/<int:month>/', SpendingView.as_view(), name='spending-list'),
]
