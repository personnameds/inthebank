from category.models import Category, CategoryGroup
from .models import ConstantBudget, ScheduledBudget
from transaction.models import Transaction
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, CreateView
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY, WEEKLY
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.urls import reverse
from calendar import monthrange

#Left in Budget
def get_budget_left(month_budget,remainder, spent):
	if remainder:
		budget_left = min(0,month_budget - spent)
	elif spent:
		budget_left = 0
	else:
		budget_left = month_budget
	return budget_left

#Constant Budget
def get_constantbudget(categorygroup, category, spent, remainder):
	if categorygroup:
		month_budget = ConstantBudget.objects.get(categorygroup=categorygroup).amount
	else:
		month_budget = ConstantBudget.objects.get(category=category).amount
	month_budget_list = [month_budget]*11
	
	month_budget_left = get_budget_left(month_budget,remainder, spent)
	
	return month_budget_list, month_budget_left

#Avg Quarter Budget
def get_avgquarterbudget(categories, category, spent, remainder, now):
	
	from_date = now.replace(day=1)
	to_date = now.replace(day=1)							
	from_date = from_date + relativedelta(months=-3)
	to_date = to_date + relativedelta(days=-1)
	
	if categories:
		month_budget = Transaction.objects.filter(category__in=categories, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
	
	else:
		month_budget = Transaction.objects.filter(category=category, date__gte=from_date, date__lte=to_date).aggregate(Sum('amount'))
	month_budget = month_budget['amount__sum'] or 0
	month_budget = month_budget/3

	month_budget_list = [month_budget]*11
	
	month_budget_left = get_budget_left(month_budget, remainder, spent)
	
	return month_budget_list, month_budget_left

#Scheduled Budget
def get_scheduledbudget(categorygroup, category, spent, remainder, now, month_list):
	

	if categorygroup:
		sb_object = ScheduledBudget.objects.get(categorygroup=categorygroup)
	else:
		sb_object = ScheduledBudget.objects.get(category=category)

	
	budget_amount = sb_object.amount
	last_date = sb_object.last_date

	#Finds payments based on last date
	#For first time, may miss a payment if last_date entered by user is not first payment that month
	#Code needs to always save last_date as the first payment that month each time
	from_date = rrule(freq=WEEKLY, interval=2, dtstart=last_date, until=now)
	from_date = [fd for fd in from_date if fd.month == now.month][0]
	sb_object.last_date = from_date

	to_date = now + relativedelta(months=11)
	to_date = to_date.replace(day=monthrange(to_date.year,to_date.month)[1])
	
	payment_list = rrule(freq=WEEKLY, interval=2, dtstart=from_date, until=to_date)					
	payment_list = [p.month for p in payment_list]
	
	if categorygroup:
		budget_amount = ScheduledBudget.objects.get(categorygroup=categorygroup).amount
	else:
		budget_amount = ScheduledBudget.objects.get(category=category).amount
	
	month_budget = payment_list.count(now.month) * budget_amount
	month_budget_left = get_budget_left(month_budget, remainder, spent)
	
	month_budget_list= [payment_list.count(m.month) * budget_amount for m in month_list[1:]]
	

	return month_budget_list, month_budget_left


class BudgetView(TemplateView):
	template_name='budget.html'


	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

# 		show_all=self.request.GET.get('option')
# 		if show_all == 'showall':
# 			show_all=True
# 		else:
# 			show_all=False

		now = datetime.now()
		month_list = list(rrule(freq=MONTHLY, count = 12, dtstart=now))
		
		budget_list=[]
		
		categorygroups = CategoryGroup.objects.all().exclude(name='Income')
		
		
		for categorygroup in categorygroups:

			categories = categorygroup.category_set.all()
			
			#Group Spending
			spent = Transaction.objects.filter(
					category__in=categories, date__month=now.month, date__year=now.year
					).aggregate(Sum('amount'))
			spent = spent['amount__sum'] or 0
			
			#Group Budget
			if categorygroup.budget_method != 'N':
				#Constant
				if categorygroup.budget_method == 'C':
					month_budget_list, budget_left = get_constantbudget(categorygroup,None, spent, categorygroup.remainder)
				#Avg over Quarter
				elif categorygroup.budget_method == 'A':
					month_budget_list, budget_left = get_avgquarterbudget(categories, None, spent, categorygroup.remainder, now)
				elif categorygroup.budget_method == 'S':
					month_budget_list, budget_left = get_scheduledbudget(categorygroup, None, spent, categorygroup.remainder, now, month_list)
			else:
				budget_left = None
				month_budget = None
				month_budget_list = None
				
			group_list=(categorygroup, spent, budget_left, month_budget_list)

			#Category Spending
			category_list=[]
			for category in categories:
				spent = Transaction.objects.filter(
					category=category, date__month=now.month, date__year=now.year
					).aggregate(Sum('amount'))
				spent = spent['amount__sum'] or 0			
			
				#Category Budget
				if category.budget_method != 'N':
					#Constant
					if category.budget_method == 'C':
						month_budget_list, budget_left = get_constantbudget(None, category, spent, category.remainder)
					#Avg over Quarter
					elif category.budget_method == 'A':
						month_budget_list, budget_left = get_avgquarterbudget(None, category, spent, category.remainder, now)
					elif category.budget_method =='S':
						month_budget_list, budget_left = get_scheduledbudget(None, category, spent, category.remainder, now, month_list)
				else:
					budget_left = None
					month_budget = None
					month_budget_list = None
				
				category_list.append((category, spent, budget_left, month_budget_list))
				
			budget_list.append((group_list,category_list))
		
		context['month_list'] = month_list
		context['budget_list'] = budget_list
		context['title'] = 'Budget for Year'
#		context['show_all'] = show_all
		
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
			
		return super(ConstantBudgetCreateView, self).form_valid(form)

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
			
		return super(ScheduledBudgetCreateView, self).form_valid(form)

	def get_success_url(self):
		return reverse('budget-list')