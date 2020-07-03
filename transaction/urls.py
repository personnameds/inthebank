from django.urls import path
from .views import TransactionImportView, ChooseFileView, TransactionListView

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
	path('import/', ChooseFileView.as_view(), name='choose-file'),
    path('import/<str:bank>/<str:filename>/', TransactionImportView.as_view(), name='transaction-import'),
]
