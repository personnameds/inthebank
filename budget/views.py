from category.models import Category, CategoryGroup
from .models import ConstantBudget, ScheduledBudget, SpecifiedBudget
from transaction.models import Transaction
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, CreateView
from datetime import timedelta, datetime
from dateutil.rrule import rrule, MONTHLY, WEEKLY
from dateutil.relativedelta import relativedelta
from inthebank.views import view_title_context_data
from django.db.models import Sum
from django.urls import reverse
from calendar import monthrange

def get_scheduledbudget(group,category,view_date):
	if group:
		sb = ScheduledBudget.objects.get(categorygroup=group)
	else:
		sb = ScheduledBudget.objects.get(category=category)
	
	budget = sb.amount
	if view_date >= sb.last_date:
		from_date = sb.last_date
	
	else:
		from_date = sb.last_date
		while from_date > view_date:
			from_date = from_date + relativedelta(weeks=-2)
		
	to_date = view_date.replace(day=monthrange(view_date.year,view_date.month)[1])
	
	#2 weeks hardcoded in
	sched_dates = rrule(freq=WEEKLY, interval=2, dtstart=from_date, until=to_date)
	sched_dates = [sd for sd in sched_dates if sd.month == view_date.month]
	
	budget = len(sched_dates) * budget
	if sched_dates[0].date() > sb.last_date:
		sb.last_date = sched_dates[0]
		sb.save()
	
	return budget

def check_specific_budget():
	pass

def get_budget(group,category,method,view_date):
	if method == 'N':
		budget = None
	elif method =='C':
		if group:
			budget = ConstantBudget.objects.get(categorygroup=group).amount
		else:
			budget = ConstantBudget.objects.get(category=category).amount
	elif method == 'A':
		from_date = view_date.replace(day=1)
		to_date = view_date.replace(day=1)
		from_date = from_date + relativedelta(months=-3)
		to_date = to_date + relativedelta(days=-1)
	
		if group:
			categories = group.category_set.all()
			budget = Transaction.objects.filter(category__in=categories, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
		else:
			budget = Transaction.objects.filter(category=category, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
		
		budget = budget['amount__sum'] or 0
		budget = budget/3

	elif method == 'S':
		budget = get_scheduledbudget(group,category,view_date)

	elif method == 'Y':
		from_date = view_date.replace(day=1)
		from_date = from_date + relativedelta(years=-1)
		to_date = from_date.replace(day=monthrange(from_date.year,from_date.month)[1])
	
		if group:
			categories = group.category_set.all()
			budget = Transaction.objects.filter(category__in=categories, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
		else:
			budget = Transaction.objects.filter(category=category, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
		
		budget = budget['amount__sum'] or 0

	return budget

class BudgetView(TemplateView):
	template_name = 'budget.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		view_title='Budget for'
		view_url='budget-list'	
		context, view_date=view_title_context_data(self, context, view_url, view_title)

		#Header and Month List
		#Hard Coded 3 Months Prior
		from_date = view_date.replace(day=1)
		to_date = from_date + timedelta(days=-1)
		from_date = from_date + relativedelta(months=-3)
		date_list = list(rrule(freq=MONTHLY, count = 4, dtstart=from_date))
		context['date_list'] = date_list

		##Does not include Credit Cards and Income
		group_list = CategoryGroup.objects.all().exclude(name='Credit Cards').exclude(name='Income')
		transaction_list = Transaction.objects.filter(date__gte=from_date,date__lte=to_date)

		full_list=[]
		for group in group_list:

			#Category List
			categories = group.category_set.all()
			category_list=[]

			#Group Budget
			group_budget = get_budget(group,None,group.budget_method,view_date)

			#Group Spent
			group_spent=[]
			for date in date_list[:3]:
				spent = transaction_list.filter(category__in=categories,date__month=date.month).aggregate(Sum('amount'))
				spent = spent['amount__sum'] or 0
				group_spent.append(spent)

			#Category Spent
			for category in categories:
				category_spent=[]
				for date in date_list[:3]:	
					spent = transaction_list.filter(category=category,date__month=date.month).aggregate(Sum('amount'))
					spent = spent['amount__sum'] or 0
					category_spent.append(spent)

				category_budget = get_budget(None,category,category.budget_method,view_date)

				#Crategory List
				category_list.append((category,category_spent,category_budget, category.budget_method, category.remainder))
	
			full_list.append(((group,group_spent,group_budget, group.budget_method, group.remainder),category_list))

		context['full_list'] = full_list
		return context

class ConstantBudgetUpdateView(UpdateView):
	model  = ConstantBudget
	template_name = 'budget_form.html'
	fields=['amount',]
	
	def get_success_url(self):
		return reverse('budget-list')

class ConstantBudgetCreateView(CreateView):
	model  = ConstantBudget
	template_name = 'budget_form.html'
	fields=['amount',]
	
	def form_valid(self, form):
		if self.kwargs['group_pk'] != 'None':
			group = CategoryGroup.objects.get(pk=self.kwargs['group_pk'])
			form.instance.categorygroup = group
		else:
			cat = Category.objects.get(pk=self.kwargs['cat_pk'])
			form.instance.category = cat
			
		return super().form_valid(form)

	def get_success_url(self):
		return reverse('budget-list')

class ScheduledBudgetUpdateView(UpdateView):
	model  = ScheduledBudget
	template_name = 'budget_form.html'
	fields=['amount','last_date']
	
	def get_success_url(self):
		return reverse('budget-list')

class ScheduledBudgetCreateView(CreateView):
	model  = ScheduledBudget
	template_name = 'budget_form.html'
	fields=['amount','last_date']
	
	def form_valid(self, form):
		if self.kwargs['group_pk'] != 'None':
			group = CategoryGroup.objects.get(pk=self.kwargs['group_pk'])
			form.instance.categorygroup = group
		else:
			cat = Category.objects.get(pk=self.kwargs['cat_pk'])
			form.instance.category = cat
			
		return super().form_valid(form)

	def get_success_url(self):
		return reverse('budget-list')

class SpecifiedBudgetCreateView(CreateView):
	model  = SpecifiedBudget
	template_name = 'specified_budget_form.html'
	fields=['amount',]

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if self.kwargs['group_pk'] != 'None':
			group = CategoryGroup.objects.get(pk=self.kwargs['group_pk'])
		else:
			category = Category.objects.get(pk=self.kwargs['cat_pk'])
			group = category.group
			context['category'] = category
        
		month = self.kwargs['month']
		year = self.kwargs['year']
		date = datetime(year, month,1)
		context['date'] = date
		context['group'] = group
		return context

	def form_valid(self, form):
		month = self.kwargs['month']
		year = self.kwargs['year']
		date = datetime(year, month,1)
		form.instance.date = date

		if self.kwargs['group_pk'] != 'None':
			group = CategoryGroup.objects.get(pk=self.kwargs['group_pk'])
			form.instance.categorygroup = group

			if SpecifiedBudget.objects.filter(categorygroup=group,date=date):
				SpecifiedBudget.objects.get(category=cat,date=date).delete()
		else:
			cat = Category.objects.get(pk=self.kwargs['cat_pk'])
			form.instance.category = cat
			if SpecifiedBudget.objects.filter(category=cat,date=date):
				SpecifiedBudget.objects.get(category=cat,date=date).delete()

		return super().form_valid(form)

	def get_success_url(self):
		return reverse('budget-list')