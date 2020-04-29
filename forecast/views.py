from django.shortcuts import render
from django.views.generic.base import TemplateView
from transaction.models import Transaction
from category.models import Category
from django.db.models import Sum

class TransactionByCategoryView(TemplateView):
	template_name = 'forecastbycategory.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		categories = Category.objects.all()
		bycategory=[]
		for category in categories:
			transaction_sum=Transaction.objects.filter(category=category).aggregate(Sum('amount'))
			bycategory.append((category,transaction_sum))
		context['bycategory_list']=bycategory
		return context