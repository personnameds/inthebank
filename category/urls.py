from django.urls import path
from .views import CategoryListView, SpendingView

urlpatterns = [
    path('', CategoryListView.as_view(), name='category-list'),
    path('spending/', SpendingView.as_view(), name='spending-list'),
    path('spending/<int:year>/<int:month>/', SpendingView.as_view(), name='spending-list'),
]
