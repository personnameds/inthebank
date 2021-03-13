from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, FormView
from .forms import FilterForm
from .models import Category, CategoryGroup
from budget.models import ConstantBudget, ScheduledBudget
from transaction.models import Transaction
from decimal import Decimal
from django.db.models import Sum
from inthebank.views import view_title_context_data
from django.urls import reverse
from django.http import HttpResponseRedirect
import datetime
from dateutil.relativedelta import relativedelta

class CategoryListView(ListView):
	model = CategoryGroup
	context_object_name = 'category_group_list'
	template_name = 'category_list.html'

class CategoryGroupUpdateView(UpdateView):
	model  = CategoryGroup
	template_name = 'category_form.html'
	fields=['name', 'budget_method', 'remainder']

	def get_success_url(self, **kwargs):
		if self.object.budget_method == 'C':
			cb = ConstantBudget.objects.filter(categorygroup=self.object)
			if cb:
				return reverse('constantbudget-update', kwargs={'pk':cb[0].pk})
			else:
				return reverse('constantbudget-create', kwargs={'group_pk':self.object.pk, 'cat_pk':None})
		elif self.object.budget_method=='S':
			sb = ScheduledBudget.objects.filter(categorygroup=self.object)
			if sb:
				return reverse('scheduledbudget-update', kwargs={'pk':sb[0].pk})
			else:
				return reverse('scheduedbudget-create', kwargs={'group_pk':self.object.pk, 'cat_pk':None})
		return reverse('budget-list')

class CategoryUpdateView(UpdateView):
	model  = Category
	template_name = 'category_form.html'
	fields=['name', 'budget_method', 'remainder']

	def get_success_url(self, **kwargs):
		if self.object.budget_method == 'C':
			cb = ConstantBudget.objects.filter(category=self.object)
			if cb:
				return reverse('constantbudget-update', kwargs={'pk':cb[0].pk})
			else:
				return reverse('constantbudget-create', kwargs={'group_pk':None, 'cat_pk':self.object.pk})
		if self.object.budget_method == 'S':
			sb = ScheduledBudget.objects.filter(category=self.object)
			if sb:
				return reverse('scheduledbudget-update', kwargs={'pk':sb[0].pk})
			else:
				return reverse('scheduledbudget-create', kwargs={'group_pk':None, 'cat_pk':self.object.pk})
		return reverse('budget-list')

class SpendingView(TemplateView):
	template_name='spending_list.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)		
		view_title='Spending by Category in'
		view_url='spending-list'
		
		context, view_date=view_title_context_data(self, context, view_url, view_title)


		##Group Category, Amount (sum of transactions), Budget
		##Table: Date, Description, Amount
		spending_list=[]
	
		#All Groups
		cat_group_list=CategoryGroup.objects.all().order_by('name')
	
		for cat_group in cat_group_list:

			#List of categories in the group
			cat_list=[]
			cat_list_in_group = Category.objects.filter(group=cat_group)
			group_sum = Transaction.objects.filter(
				category__in=cat_list_in_group,
				date__month=view_date.month,
				date__year=view_date.year).aggregate(Sum('amount'))
		
			#Each Category in the group
			for cat in cat_list_in_group:
				tran_list=Transaction.objects.filter(
					category=cat,
					date__month=view_date.month,
					date__year=view_date.year).order_by('date')
				cat_sum=tran_list.aggregate(Sum('amount'))
			
				cat_list.append((cat,cat_sum,tran_list))
			
			group_list=(cat_group,group_sum,cat_list)
			spending_list.append(group_list)	

		context['spending_list']=spending_list
	
		return context

class SpendingFilterView(TemplateView):
	template_name='spending_list.html'
	
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		from_date = self.kwargs['from_date']
		to_date = self.kwargs['to_date']
		group = self.kwargs['group']

		if group:
			cat_group_list = CategoryGroup.objects.filter(pk=group).order_by('name')
		else:
			cat_group_list=CategoryGroup.objects.all().order_by('name')

		spending_list=[]
	
		for cat_group in cat_group_list:

			#List of categories in the group
			cat_list=[]
			cat_list_in_group = Category.objects.filter(group=cat_group)
			group_sum = Transaction.objects.filter(
				category__in=cat_list_in_group,
				date__gte=from_date,
				date__lte=to_date).aggregate(Sum('amount'))
		
			#Each Category in the group
			for cat in cat_list_in_group:
				tran_list=Transaction.objects.filter(
					category=cat,
					date__gte=from_date,
					date__lte=to_date).order_by('date')
				cat_sum=tran_list.aggregate(Sum('amount'))
			
				cat_list.append((cat,cat_sum,tran_list))
			
			group_list=(cat_group,group_sum,cat_list)
			spending_list.append(group_list)	

		context['spending_list']=spending_list
	
		return context

class SpendingFilterFormView(FormView):
	template_name = 'filter_form.html'
	form_class = FilterForm

	def get_initial(self):
		initial = super().get_initial()
		initial['to_date'] = datetime.date.today()
		initial['from_date'] = datetime.date.today() - relativedelta(years=1)
		return initial

	def form_valid(self, form):
		from_date, to_date = form.cleaned_data['from_date'], form.cleaned_data['to_date']
		group = form.cleaned_data['category_group']

		return HttpResponseRedirect(
				reverse('spending-filter-list', kwargs={'from_date':from_date,'to_date':to_date,'group':group.pk})
		)