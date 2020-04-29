from django.urls import path
from .views import TransactionImportView, ChooseFileView

urlpatterns = [
    path('', ChooseFileView.as_view(), name='choose-file'),
    path('import/<str:bank>/<str:filename>/', TransactionImportView.as_view(), name='transaction-import'),
]
