from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from budget.models import CategoryBudget, BudgetForm
from category.models import Category
from transaction.models import Transaction
from django.db.models import Sum
import datetime
from dateutil.relativedelta import relativedelta #external library/extension python-dateutil
from decimal import Decimal
from django.urls import reverse

class BudgetByCategoryView(TemplateView):
	template_name = 'budgetbycategory.html'
	
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

		budget_list=[]
		category_list=Category.objects.all().order_by('category__group__name','category__name')		
		categorybudget_list=CategoryBudget.objects.all()
		for categorybudget in categorybudget_list:
			category=categorybudget.category
			category_sum=Transaction.objects.filter(
				category=category,
				date__month=view_date.month,
				date__year=view_date.year).aggregate(Sum('amount'))
			budget_item=[category,category_sum,categorybudget]
			budget_list.append(budget_item)	

		context['budget_list']=budget_list

		return context

class AddBudget(FormView):
	template_name = 'addbudget.html'
	form_class = BudgetForm
	success_url ='/notsetup'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		category=Category.objects.get(pk=self.kwargs['cat_id'])
		context['category']=category
		return context

	def form_valid(self, form):
		category=Category.objects.get(pk=self.kwargs['cat_id'])
		categorybudget=CategoryBudget(
			category=category,
			amount=Decimal(form.cleaned_data['amount']),
			)
		categorybudget.save()
		return super().form_valid(form)

	def get_success_url(self, **kwargs):
		return reverse('spendbycat-list')


