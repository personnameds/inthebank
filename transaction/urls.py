from django.urls import path
from .views import TransactionImportView, ChooseFileView, TransactionListView, TransactionUpdateView, ScheduledTransactionListView

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('<int:year>/<int:month>/', TransactionListView.as_view(), name='transaction-list'),
    path('update/<int:pk>/', TransactionUpdateView.as_view(), name='transaction-update'),
	path('import/', ChooseFileView.as_view(), name='choose-file'),
    path('import/<str:bank>/<str:filename>/', TransactionImportView.as_view(), name='transaction-import'),
    path('scheduled/', ScheduledTransactionListView.as_view(), name='scheduled-list'),
]
