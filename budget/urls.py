from django.urls import path
from .views import BudgetView, ConstantBudgetUpdateView, ConstantBudgetCreateView
from .views import ScheduledBudgetUpdateView, ScheduledBudgetCreateView
from .views import SpecifiedBudgetCreateView

urlpatterns = [
    path('', BudgetView.as_view(), name='budget-list'),
    path('<int:year>/<int:month>/', BudgetView.as_view(), name='budget-list'),
    path('update/constantbudget/<int:pk>/', ConstantBudgetUpdateView.as_view(), name='constantbudget-update'),    
    path('create/constantbudget/<group_pk>/<cat_pk>/', ConstantBudgetCreateView.as_view(), name='constantbudget-create'),   
    path('update/scheduledbudget/<int:pk>/', ScheduledBudgetUpdateView.as_view(), name='scheduledbudget-update'),    
    path('create/scheduledbudget/<group_pk>/<cat_pk>/', ScheduledBudgetCreateView.as_view(), name='scheduledbudget-create'), 
    path('create/specifiedbudget/<group_pk>/<cat_pk>/<int:year>/<int:month>/', SpecifiedBudgetCreateView.as_view(), name='specifiedbudget-create'), 

]
