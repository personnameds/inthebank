from django.urls import path
from .views import BudgetView, AddGroupBudgetFormView, AddCatBudgetFormView

urlpatterns = [
    path('', BudgetView.as_view(), name='budget-list'),
    path('<int:year>/<int:month>/', BudgetView.as_view(), name='budget-list'),
    path('addgroupbudget/<pk>/', AddGroupBudgetFormView.as_view(), name='add-group-budget'),
    path('addcatbudget/<pk>/', AddCatBudgetFormView.as_view(), name='add-cat-budget'),
]
