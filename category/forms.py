from django import forms
from category.models import CategoryGroup

class FilterForm(forms.Form):
	from_date = forms.DateField(help_text='yyyy-mm-dd', widget=forms.DateInput)
	to_date = forms.DateField(help_text='yyyy-mm-dd', widget=forms.DateInput)
	category_group = forms.ModelChoiceField(queryset=CategoryGroup.objects.all(), empty_label=None)