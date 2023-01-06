from category.models import Category, CategoryGroup
from .models import ConstantBudget, ScheduledBudget, SpecificBudget
from .models import SpecificBudgetForm
from transaction.models import Transaction
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, CreateView, FormView
from datetime import date
from dateutil.rrule import rrule, MONTHLY, WEEKLY
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.urls import reverse
from calendar import monthrange

#Spent
def get_spent(categories,category,today):
	if categories:
		spent = Transaction.objects.filter(
					category__in=categories, date__month=today.month, date__year=today.year
					).aggregate(Sum('amount'))
	elif category:
		spent = Transaction.objects.filter(
				category=category, date__month=today.month, date__year=today.year
					).aggregate(Sum('amount'))
	spent = spent['amount__sum'] or 0
	return spent

#Check Specific Budget month list
def check_specific_budget(month_budget, month_budget_list, month_list, categorygroup, category):
	#Current Month
	sp_current = SpecificBudget.objects.filter
	today = date.today()
	month = today.replace(day=1)
	#Check month_list
	if categorygroup:
		specific_budget_list = SpecificBudget.objects.filter(categorygroup=categorygroup, budget_month__in=month_list)
		specific_budget_current = SpecificBudget.objects.filter(categorygroup=categorygroup, budget_month=month)
	else:
		specific_budget_list = SpecificBudget.objects.filter(category=category, budget_month__in=month_list)
		specific_budget_current = SpecificBudget.objects.filter(category=category, budget_month=month)

	if specific_budget_current:
		month_budget = specific_budget_current[0].amount

	if specific_budget_list:
		for sb in specific_budget_list:
			for i in range(len(month_budget_list)):
				if month_budget_list[i][0].date() == sb.budget_month:
					month_budget_list[i][1] = sb.amount
					month_budget_list[i].insert(2,'*')
	return month_budget, month_budget_list

#Left in Budget
def get_budget_left(month_budget,remainder, spent):
	if remainder:
		if month_budget < 0:
			budget_left = min(0,month_budget - spent)
		else:
			budget_left = month_budget - spent
	elif spent:
		budget_left = 0
	else:
		budget_left = month_budget
	return budget_left

#Constant Budget for Year
def get_constantbudget(categorygroup, category, spent, remainder, month_list):
	if categorygroup:
		month_budget = ConstantBudget.objects.get(categorygroup=categorygroup).amount
	else:
		month_budget = ConstantBudget.objects.get(category=category).amount
	
	for m in month_list:
		month_budget_list = [[m,month_budget] for m in month_list[1:]]
	
	month_budget, month_budget_list = check_specific_budget(month_budget, month_budget_list, month_list, categorygroup, category)
	
	month_budget_left = get_budget_left(month_budget,remainder, spent)

	return month_budget_list, month_budget_left

#Constant Budget for Month
def get_month_constantbudget(categorygroup, category):
	if categorygroup:
		month_budget = ConstantBudget.objects.get(categorygroup=categorygroup).amount
	else:
		month_budget = ConstantBudget.objects.get(category=category).amount
	return month_budget

#Avg Quarter Budget for Year
def get_avgquarterbudget(categories, categorygroup, category, spent, today, remainder, month_list):

	from_date = today.replace(day=1)
	to_date = today.replace(day=1)							
	from_date = from_date + relativedelta(months=-3)
	to_date = to_date + relativedelta(days=-1)
	
	if categories:
		month_budget = Transaction.objects.filter(category__in=categories, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
	
	else:
		month_budget = Transaction.objects.filter(category=category, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
	month_budget = month_budget['amount__sum'] or 0
	month_budget = month_budget/3

	for m in month_list:
		month_budget_list = [[m,month_budget] for m in month_list[1:]]
	
	month_budget, month_budget_list = check_specific_budget(month_budget, month_budget_list, month_list, categorygroup, category)

	month_budget_left = get_budget_left(month_budget, remainder, spent)
	
	return month_budget_list, month_budget_left

#Avg Quarter Budget for Month
def get_month_avgquarterbudget(categories, category,today):
	from_date = today.replace(day=1)
	to_date = today.replace(day=1)							
	from_date = from_date + relativedelta(months=-3)
	to_date = to_date + relativedelta(days=-1)
	
	if categories:
		month_budget = Transaction.objects.filter(category__in=categories, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
	else:
		month_budget = Transaction.objects.filter(category=category, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
	month_budget = month_budget['amount__sum'] or 0
	month_budget = month_budget/3

	return month_budget

#Scheduled Budget for Year
def get_scheduledbudget(categorygroup, category, spent, today, remainder, month_list):
	if categorygroup:
		sb_object = ScheduledBudget.objects.get(categorygroup=categorygroup)
	else:
		sb_object = ScheduledBudget.objects.get(category=category)

	budget_amount = sb_object.amount
	last_date = sb_object.last_date

	#Finds payments based on last date
	#For first time, may miss a payment if last_date entered by user is not first payment that month
	#Code needs to always save last_date as the first payment that month each time
	last_day_month = today.replace(day=monthrange(today.year,today.month)[1])
	from_date = rrule(freq=WEEKLY, interval=2, dtstart=last_date, until=last_day_month)
	from_date = [fd for fd in from_date if fd.month == today.month][0]
	sb_object.last_date = from_date

	to_date = today + relativedelta(months=11)
	to_date = to_date.replace(day=monthrange(to_date.year,to_date.month)[1])
	
	payment_list = rrule(freq=WEEKLY, interval=2, dtstart=from_date, until=to_date)					
	payment_list = [p.month for p in payment_list]
	
	if categorygroup:
		budget_amount = ScheduledBudget.objects.get(categorygroup=categorygroup).amount
	else:
		budget_amount = ScheduledBudget.objects.get(category=category).amount

	month_budget = payment_list.count(today.month) * budget_amount
	month_budget_left = get_budget_left(month_budget, remainder, spent)
	
	month_budget_list= [[m,payment_list.count(m.month) * budget_amount] for m in month_list[1:]]
	month_budget, month_budget_list = check_specific_budget(month_budget, month_budget_list, month_list, categorygroup, category)
	
	return month_budget_list, month_budget_left

#Scheduled Budget for Month
def get_month_scheduledbudget(categorygroup, category, today):
	if categorygroup:
		sb_object = ScheduledBudget.objects.get(categorygroup=categorygroup)
	else:
		sb_object = ScheduledBudget.objects.get(category=category)

	budget_amount = sb_object.amount
	last_date = sb_object.last_date

	last_day_month = today.replace(day=monthrange(today.year,today.month)[1])
	from_date = rrule(freq=WEEKLY, interval=2, dtstart=last_date, until=last_day_month)
	from_date = [fd for fd in from_date if fd.month == today.month]

	sb_object.last_date = from_date[0]
	sb_object.save()

	month_budget = len(from_date) * budget_amount

	return month_budget


#Last Year Budget for Year
def get_lastyearbudget(categories, categorygroup, category, spent, today, remainder, month_list):
	
	from_date = today.replace(day=1)
	from_date = from_date + relativedelta(years=-1)
	to_date = today + relativedelta(years=-1)
	to_date = to_date.replace(day=monthrange(to_date.year,to_date.month)[1])

	month_budget_list = []
	if categories:
		month_budget = Transaction.objects.filter(category__in=categories, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
		for m in month_list[1:]:
			year_ago = m + relativedelta(years=-1)			
			mb = Transaction.objects.filter(category__in=categories, date__month=year_ago.month, date__year=year_ago.year).aggregate(Sum('amount'))
			month_budget_list.append([m,mb['amount__sum'] or 0])
	else:
		month_budget = Transaction.objects.filter(category=category, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
		
		for m in month_list[1:]:
			year_ago = m + relativedelta(years=-1)
			mb = Transaction.objects.filter(category=category, date__month=year_ago.month, date__year=year_ago.year).aggregate(Sum('amount'))
			mb = mb['amount__sum'] or 0
			month_budget_list.append([m,mb])

	month_budget=month_budget['amount__sum'] or 0

	month_budget, month_budget_list = check_specific_budget(month_budget, month_budget_list, month_list, categorygroup, category)
	
	month_budget_left = get_budget_left(month_budget, remainder, spent)

	return month_budget_list, month_budget_left

#Last Year Budget for Month
def get_month_lastyearbudget(categories, category, today):
	
	from_date = today.replace(day=1)
	from_date = from_date + relativedelta(years=-1)
	to_date = today + relativedelta(years=-1)
	to_date = to_date.replace(day=monthrange(to_date.year,to_date.month)[1])

	if categories:
		month_budget = Transaction.objects.filter(category__in=categories, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
	else:
		month_budget = Transaction.objects.filter(category=category, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))

	month_budget = month_budget['amount__sum'] or 0

	return month_budget

#Get the Budget - Main Function
def get_budget(today, month_list):
	budget_list=[]
	categorygroups = CategoryGroup.objects.all().exclude(name='Income').exclude(name='None').exclude(name='Credit Cards')

	for categorygroup in categorygroups:

		categories = categorygroup.category_set.all()
		
		#Group Spending
		spent = get_spent(categories, None, today) 
		
		#Group Budget
		if categorygroup.budget_method != 'N':
			#Constant
			if categorygroup.budget_method == 'C':
				month_budget_list, budget_left = get_constantbudget(categorygroup,None, spent, categorygroup.remainder, month_list)
			#Avg over Quarter
			elif categorygroup.budget_method == 'A':
				month_budget_list, budget_left = get_avgquarterbudget(categories, categorygroup, None, spent, today, categorygroup.remainder, month_list)
			#Scheduled
			elif categorygroup.budget_method == 'S':
				month_budget_list, budget_left = get_scheduledbudget(categorygroup, None, spent, today, categorygroup.remainder, month_list)
			#Last Year
			elif categorygroup.budget_method == 'Y':
				month_budget_list, budget_left = get_lastyearbudget(categories, categorygroup, None, spent, today, categorygroup.remainder, month_list)
		else:
			budget_left = None
			month_budget_list = None
			
		group_list=(categorygroup, spent, budget_left, month_budget_list)

		#Category Spending
		category_list=[]
		for category in categories:
			spent = get_spent(None, category, today)		
		
			#Category Budget
			if category.budget_method != 'N':
				#Constant
				if category.budget_method == 'C':
					month_budget_list, budget_left = get_constantbudget(None, category, spent, category.remainder, month_list)
				#Avg over Quarter
				elif category.budget_method == 'A':
					month_budget_list, budget_left = get_avgquarterbudget(None, None, category, spent, today, category.remainder, month_list)
				#Scheduled
				elif category.budget_method =='S':
					month_budget_list, budget_left = get_scheduledbudget(None, category, spent, today, category.remainder, month_list)
				#Last Year
				elif category.budget_method == 'Y':
					month_budget_list, budget_left = get_lastyearbudget(None, None, category, spent, today, category.remainder, month_list)
			else:
				budget_left = None
				month_budget_list = None
			
			category_list.append((category, spent, budget_left, month_budget_list))
			
		budget_list.append((group_list,category_list))
	
	return budget_list

class BudgetView(TemplateView):
	template_name='budget.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		today = date.today()
		first_of_month = today.replace(day=1)
		month_list = list(rrule(freq=MONTHLY, count = 12, dtstart=first_of_month))

		budget_list = get_budget(today, month_list)

		context['month_list'] = month_list
		context['budget_list'] = budget_list
		context['title'] = 'Budget for Year'

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

class SpecificBudgetFormView(FormView):
	template_name = 'budget_form.html'
	fields=['amount','budget_month']
	form_class= SpecificBudgetForm

	def get_initial(self):
		initial = super().get_initial()
		
		if self.kwargs['group_pk'] != 'None':
			group = CategoryGroup.objects.get(pk=self.kwargs['group_pk'])
			cat = None
		else:
			cat = Category.objects.get(pk=self.kwargs['cat_pk'])
			group = None
		
		month = self.kwargs['month']
		year = self.kwargs['year']
		budget_month = date(year,month,1)

		spbudget = SpecificBudget.objects.filter(category= cat, categorygroup=group, budget_month=budget_month)

		if spbudget:
			initial['amount'] = spbudget = spbudget[0].amount

		return initial
	
	def form_valid(self, form):
		if self.kwargs['group_pk'] != 'None':
			group = CategoryGroup.objects.get(pk=self.kwargs['group_pk'])
			cat = None
		else:
			cat = Category.objects.get(pk=self.kwargs['cat_pk'])
			group = None
		
		month = self.kwargs['month']
		year = self.kwargs['year']
		budget_month = date(year,month,1)
		
		spbudget = SpecificBudget.objects.filter(category= cat, categorygroup=group, budget_month=budget_month)

		if spbudget:
			if form.cleaned_data['remove'] == True:
				spbudget[0].delete()
			else:
				spbudget = spbudget[0]
				spbudget.amount = form.instance.amount or 0
				spbudget.save()
		else:
			spbudget = SpecificBudget(
				category = cat,
				categorygroup = group,
				amount = form.instance.amount or 0,
				budget_month = budget_month,
			)	
			spbudget.save()
		
		return super().form_valid(form)

	def get_success_url(self):
		return reverse('budget-list')
