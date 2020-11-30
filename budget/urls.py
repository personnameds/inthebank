from django.urls import path
from .views import BudgetView, CategoryGroupBudgetUpdateView, CategoryBudgetUpdateView

urlpatterns = [
    path('', BudgetView.as_view(), name='budget-list'),
    path('<int:year>/<int:month>/', BudgetView.as_view(), name='budget-list'),
    path('update/categorygroup/<int:pk>/', CategoryGroupBudgetUpdateView.as_view(), name='categorygroupbudget-update'),
    path('update/category/<int:pk>/', CategoryBudgetUpdateView.as_view(), name='categorybudget-update'),
]
