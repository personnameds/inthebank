from django import forms 
from .models import Transaction
from category.models import Category, CategoryGroup
from account.models import Account
from category.fields import GroupedModelChoiceField
from django.conf import settings

class ChooseFileForm(forms.Form):
	#filename=forms.CharField(max_length=50)
	account = forms.ModelChoiceField(queryset=Account.objects.all())
	balance = forms.DecimalField(max_digits=8, decimal_places=2)
	csvfile = forms.FileField()


class TransactionForm(forms.ModelForm):
	date = forms.DateField(label=False)
	description = forms.CharField(max_length=250, label=False)
	amount = forms.DecimalField(max_digits=8, decimal_places=2, label=False)
	category = GroupedModelChoiceField(
		queryset=Category.objects.exclude(group=None).order_by('group__name','name'),
		choices_groupby='group',
		required=False
	)
		
	class Meta:
		model = Transaction
		fields = ['date', 'description', 'amount', 'category']
		
TransactionFormSet = forms.formset_factory(TransactionForm, extra=0)