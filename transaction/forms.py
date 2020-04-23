from django.forms import ModelForm, formset_factory, ModelChoiceField
from .models import Transaction


class TransactionForm(ModelForm):

	class Meta:
		model = Transaction
		fields = ['date', 'description', 'amount', 'category']
		
TransactionFormSet = formset_factory(TransactionForm, max_num=0)
