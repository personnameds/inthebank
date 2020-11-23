from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from category.models import Category, CategoryGroup
from transaction.models import Transaction
from django.db.models import Sum
from decimal import Decimal
from django.urls import reverse
from inthebank.views import view_date_control

class AddGroupBudgetFormView(UpdateView):
	template_name= 'budget_form.html'
	model=CategoryGroup
	fields=['budget']
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		context['budgettitle']=self.object.name
		return context

	def get_success_url(self, **kwargs):
		return reverse('budget-list')

class AddCatBudgetFormView(UpdateView):
	template_name= 'budget_form.html'
	model=Category
	fields=['budget']
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		context['budgettitle']=self.object.name
		return context

	def get_success_url(self, **kwargs):
		return reverse('budget-list')


class BudgetView(TemplateView):
	template_name = 'budget_list.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		## For Title and Choosing Viewing Date			
		if self.kwargs:
			return_control=view_date_control(self.kwargs['year'],self.kwargs['month'])
		else:
			return_control=view_date_control(None, None)

		view_date = return_control['view_date']
		context['title']='Budget by Category for'	
		context['view_url']='budget-list'
		context['prev']=return_control['prev']
		context['next']=return_control['next']
		context['view_date']=view_date
		## End of Title

		budget_list=[]

		#All groups
		cat_group_list=CategoryGroup.objects.all().order_by('name')		
		#For each group
		for cat_group in cat_group_list:
		
			#List of categories in the group
			cat_list=[]
			cat_list_in_group = Category.objects.filter(group=cat_group)
			group_sum = Transaction.objects.filter(
				category__in=cat_list_in_group,
				date__month=view_date.month,
				date__year=view_date.year).aggregate(Sum('amount'))
			for cat_item in cat_list_in_group:
				cat_sum=Transaction.objects.filter(
					category=cat_item,
					date__month=view_date.month,
					date__year=view_date.year).aggregate(Sum('amount'))
				cat_list.append((cat_item,cat_sum))
			
			group_list=(cat_group,group_sum,cat_list)
			budget_list.append(group_list)
			
		context['budget_list']=budget_list
		return context
