from django.db import models
from category.models import Category

class CategoryBudget(models.Model):
	category=models.ForeignKey(Category, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=8, decimal_places=2)
	
	def __str__(self):
		return '%s budget for %s' %(self.amount, self.category)
