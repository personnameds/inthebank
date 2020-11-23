from django.db import models

class CategoryGroup(models.Model):
	name = models.CharField(max_length=50, blank=True, null=True)
	budget = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

	def __str__(self):
		return '%s' %self.name

	class Meta:
		verbose_name='Category Group'
	

class Category(models.Model):
	name = models.CharField(max_length=50, blank=True)
	group = models.ForeignKey(CategoryGroup, on_delete=models.PROTECT, blank=True, null=True)
	budget = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
	
	def __str__(self):
		return '%s' %self.name
	
	class Meta:
		verbose_name_plural = 'Categories'
