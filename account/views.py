from .models import Account, CreditCard
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView

class AccountView(ListView):
    model = Account
    context_object_name = 'account_list'
    template_name = 'homepage.html'

class AccountUpdateView(UpdateView):
    model = Account
    fields = ['balance']
    template_name = 'generic_update_form.html'
    success_url = '/'

class CreditCardUpdateView(UpdateView):
    model = CreditCard
    fields = ['statement_balance','bill_date','payment_scheduled_date','payment_scheduled_amount']
    template_name = 'generic_update_form.html'
    success_url = '/'