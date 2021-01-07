from django.db import models

class Account(models.Model):
	name = models.CharField(max_length=50)
	balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
	last_update = models.DateField(blank=True)

	def __str__(self):
		return "%s %s %s" %(self.name, self.balance, self.last_update)