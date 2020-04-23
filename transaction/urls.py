from django.urls import path
from .views import TransactionImportView

urlpatterns = [
    path('', TransactionImportView.as_view(), name='transaction-import'),
]
