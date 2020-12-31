from django.db import models
from django.forms import ModelForm, BooleanField
from category.models import Category, CategoryGroup

	
class ConstantBudget(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
	categorygroup = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE, null=True, blank=True)
	amount = models.DecimalField(max_digits=8, decimal_places=2)

	def __str__(self):
		return "%s %s %s" %(self.categorygroup, self.category, self.amount)

class ScheduledBudget(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
	categorygroup = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE, null=True, blank=True)
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	last_date = models.DateField(help_text='YYYY-MM-DD Important: Make sure last date is first one that month')

	def __str__(self):
		return "%s %s %s %s" %(self.categorygroup, self.category, self.amount, self.last_date)

class SpecificBudget(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
	categorygroup = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE, null=True, blank=True)
	amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
	budget_month = models.DateField()

	def __str__(self):
		return "%s %s %s %s" %(self.categorygroup, self.category, self.amount, self.budget_month)

class SpecificBudgetForm(ModelForm):
	remove = BooleanField(initial=False, required=False)
	class Meta:
		model = SpecificBudget
		fields = ['amount',]