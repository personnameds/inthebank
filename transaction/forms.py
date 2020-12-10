from django import forms 
from .models import Transaction
from category.models import Category, CategoryGroup
from category.fields import GroupedModelChoiceField
from django.conf import settings

BANK_CHOICES = (
	('TD','TD CanadaTrust'),
	('PC','President Choice'),
	)

class ChooseFileForm(forms.Form):
	filename=forms.CharField(max_length=50)
	bank=forms.ChoiceField(choices=BANK_CHOICES)
#	filepath = forms.FilePathField(path=settings.BASE_DIR+'/csvfiles', match=".*\.csv$")

class TransactionForm(forms.ModelForm):
	date = forms.DateField(label=False)
	description = forms.CharField(max_length=250, label=False)
	amount = forms.DecimalField(max_digits=8, decimal_places=2, label=False)
	category = GroupedModelChoiceField(
		queryset=Category.objects.exclude(group=None).order_by('group__name','name'), ##Untested
		choices_groupby='group',
		required=False
	)
	#category = forms.ModelChoiceField(queryset=Category.objects.all(), label=False)
		
	class Meta:
		model = Transaction
		fields = ['date', 'description', 'amount', 'category']
		
TransactionFormSet = forms.formset_factory(TransactionForm, max_num=0)