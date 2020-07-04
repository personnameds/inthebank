from django.views.generic import ListView
from django.views.generic.base import TemplateView
from .models import Category
from budget.models import CategoryBudget
from transaction.models import Transaction
import datetime
from dateutil.relativedelta import relativedelta #external library/extension python-dateutil
from decimal import Decimal
from django.db.models import Sum

class CategoryListView(ListView):
	model = Category
	template_name = 'spendbycat.html'

class SpendingByCategoryView(TemplateView):
	template_name='spendbycat.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		today=datetime.date.today()

		if self.kwargs:
			year=self.kwargs['year']
			month = self.kwargs['month']
			view_date=datetime.date(year,month,1)
			prev=view_date + relativedelta(months=-1)
			if view_date.month != today.month or view_date.year != today.year:
				next = view_date + relativedelta(months=+1)
			else:
				next = None
		else: #Must be today
			view_date=datetime.date.today()
			prev=view_date + relativedelta(months=-1)
			next = None

		context['prev']=prev
		context['next']=next
		context['view_date']=view_date

		spendbycat_list=[]
		
		category_list=Category.objects.all()
		for category in category_list:
			category_sum=Transaction.objects.filter(
				category=category,
				date__month=view_date.month,
				date__year=view_date.year).aggregate(Sum('amount'))
			budget=CategoryBudget.objects.filter(category=category)
			category_item=[category,category_sum,budget]
			spendbycat_list.append(category_item)	

		context['spendbycat_list']=spendbycat_list

		return context










