from django.db import models
from category.models import Category, CategoryGroup
	
class ConstantBudget(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
	categorygroup = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE, null=True, blank=True)
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	remainder = models.BooleanField(default=True)
	
	def __str__(self):
		return "%s %s %s %s" %(self.categorygroup, self.category, self.amount, self.remainder)

##I don't need an Average Budget as it is just a calculation, only here because of Remainder
class AvgQuarterBudget(models.Model):
	category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
	categorygroup = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE, null=True, blank=True)
	remainder = models.BooleanField(default=True)
	
	def __str__(self):
		return "%s %s %s" %(self.categorygroup, self.category, self.remainder)