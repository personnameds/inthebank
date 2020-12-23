from django.urls import path
from .views import BudgetView#, BudgetFormView

urlpatterns = [
    path('', BudgetView.as_view(), name='budget-list'),
	#path('update/<int:pk>/', BudgetFormView.as_view(), name='budget-form'),
]
