from django.urls import path
from .views import BudgetView, ConstantBudgetUpdateView, ConstantBudgetCreateView
from .views import ScheduledBudgetUpdateView, ScheduledBudgetCreateView, SpecificBudgetFormView

urlpatterns = [
    path('', BudgetView.as_view(), name='budget-list'),
    path('update/c/<int:pk>/', ConstantBudgetUpdateView.as_view(), name='constantbudget-update'),    
    path('create/c/<group_pk>/<cat_pk>/', ConstantBudgetCreateView.as_view(), name='constantbudget-create'),   
    path('update/s/<int:pk>/', ScheduledBudgetUpdateView.as_view(), name='scheduledbudget-update'),    
    path('create/s/<group_pk>/<cat_pk>/', ScheduledBudgetCreateView.as_view(), name='scheduledbudget-create'), 
    path('update/sp/<group_pk>/<cat_pk>/<int:month>/<int:year>/', SpecificBudgetFormView.as_view(), name='specificbudget-form'), 
]
