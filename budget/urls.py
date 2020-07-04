from django.urls import path
from .views import BudgetByCategoryView

urlpatterns = [
    path('', BudgetByCategoryView.as_view(), name='budgetbycategory-list'),
    path('<int:year>/<int:month>/', BudgetByCategoryView.as_view(), name='budgetbycategory-list'),
]
