from django import forms
from category.models import CategoryGroup

class FilterForm(forms.Form):
	from_date = forms.DateField(help_text='yyyy-mm-dd', widget=forms.DateInput,required = False)
	to_date = forms.DateField(help_text='yyyy-mm-dd', widget=forms.DateInput,required = False)
	category_group = forms.ModelChoiceField(queryset=CategoryGroup.objects.all(),required=False)