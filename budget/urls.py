from django.urls import path
from .views import BudgetByCategoryView, AddBudget

urlpatterns = [
    path('', BudgetByCategoryView.as_view(), name='budgetbycategory-list'),
    path('<int:year>/<int:month>/', BudgetByCategoryView.as_view(), name='budgetbycategory-list'),
    path('add/<int:cat_id>', AddBudget.as_view(), name='add-budget'),
]
