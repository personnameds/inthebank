from django.db import models
from category.models import Category, CategoryGroup

class Envelope(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    categorygroup = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField()
    carryover = models.DecimalField(max_digits=8, decimal_places=2)
        
    def __str__(self):
        return "%s %s %s" %(self.categorygroup, self.category, self.amount)