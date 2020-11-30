from django.urls import path
from .views import CategoryListView, SpendingView, CategoryCreateView

urlpatterns = [
    path('', CategoryListView.as_view(), name='category-list'),
    path('create/<int:group_pk>/', CategoryCreateView.as_view(), name='category-create'),
    path('spending/', SpendingView.as_view(), name='spending-list'),
    path('spending/<int:year>/<int:month>/', SpendingView.as_view(), name='spending-list'),
]
