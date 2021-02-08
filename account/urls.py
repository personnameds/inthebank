from django.urls import path
from .views import AccountView, AccountUpdateView, CreditCardUpdateView

urlpatterns = [
    path('', AccountView.as_view(), name='homepage-index'),
    path('accountupdate/<int:pk>/', AccountUpdateView.as_view(), name='account-update'),
    path('creditcardupdate/<int:pk>/', CreditCardUpdateView.as_view(), name='creditcard-update'),
]
