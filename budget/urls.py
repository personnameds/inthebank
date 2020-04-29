from django.urls import path
from .views import BudgetByCategoryView

urlpatterns = [
    path('', BudgetByCategoryView.as_view(), name='BudgetByCategory'),
]
