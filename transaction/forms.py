from django import forms 
from .models import Transaction

BANK_CHOICES = (
	('TD','TD CanadaTrust'),
	('PC','President Choice'),
	)

class ChooseFileForm(forms.Form):
	filename=forms.CharField(max_length=50)
	bank=forms.ChoiceField(choices=BANK_CHOICES)
	

class TransactionForm(forms.ModelForm):

	class Meta:
		model = Transaction
		fields = ['date', 'description', 'amount', 'category']
		
TransactionFormSet = forms.formset_factory(TransactionForm, max_num=0)
