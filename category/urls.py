from django.urls import path
from .views import CategoryListView, SpendingByCategoryView

urlpatterns = [
    path('', CategoryListView.as_view(), name='category-display'),
    path('spending/', SpendingByCategoryView.as_view(), name='spendbycat-list'),
    path('spending/<int:year>/<int:month>/', SpendingByCategoryView.as_view(), name='spendbycat-list'),
]
