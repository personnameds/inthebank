from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from budget.models import CategoryBudget, BudgetForm
from category.models import Category
from transaction.models import Transaction
from django.db.models import Sum
from decimal import Decimal
from django.urls import reverse
from inthebank.views import view_date_control

class BudgetByCategoryView(TemplateView):
	template_name = 'budgetbycategory.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		## For Title and Choosing Viewing Date			
		if self.kwargs:
			return_control=view_date_control(self.kwargs['year'],self.kwargs['month'])
		else:
			return_control=view_date_control(None, None)

		view_date = return_control['view_date']
		context['title']='Budget by Category for '	
		context['view_url']='budgetbycategory-list'
		context['prev']=return_control['prev']
		context['next']=return_control['next']
		context['view_date']=view_date
		## End of Title

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

		no_budget_list=Transaction.objects.filter(
				date__month=view_date.month,
				date__year=view_date.year,
				).exclude(category__in=categorybudget_list.values('category'))##.aggregate(Sum('amount'))

		context['budget_list']=budget_list
		context['no_budget_list']=no_budget_list

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


