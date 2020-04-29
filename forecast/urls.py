from django.urls import path
from .views import TransactionByCategoryView

urlpatterns = [
    path('', TransactionByCategoryView.as_view(), name='TransactionByCategory'),
]
