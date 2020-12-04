from .forms import TransactionFormSet, ChooseFileForm, TransactionForm
from .models import Transaction, ScheduledTransaction, SavedTransaction
from category.models import Category
import csv
import datetime
from dateutil.relativedelta import relativedelta, MO, TU, WE #external library/extension python-dateutil
from decimal import Decimal
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse
from inthebank.views import view_title_context_data

HOLIDAY = [(1,1),]



#For Viewing all Transactions
class TransactionListView(ListView):
	model=Transaction
	template_name='transaction_list.html'
	context_object_name='transaction_list'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		view_title='Transactions for '
		view_url='transaction-list'	
		
		context, view_date=view_title_context_data(self, context, view_url, view_title)
		
		return context
	
	def get_queryset(self):
		if self.kwargs:
			year=self.kwargs['year']
			month = self.kwargs['month']
			view_date=datetime.date(year,month,1)
		else:
			view_date=datetime.date.today()
		queryset=Transaction.objects.filter(date__month=view_date.month,date__year=view_date.year).order_by('-date')
		return queryset

#For Updating/Editing Transactions
class TransactionUpdateView(UpdateView):
	model=Transaction
	template_name = 'transaction_form.html'	
	form_class = TransactionForm

	def get_success_url(self, **kwargs):
		next=self.request.GET.get('next','/')
		return next

class ScheduledTransactionListView(ListView):
	model=ScheduledTransaction
	template_name='scheduled_list.html'
	context_object_name='scheduled_list'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title']='Scheduled Transactions'		
		return context



#Import Function, enter file name
#Make this a selection window in future
#Only works in home directory
class ChooseFileView(FormView):
	template_name = 'choosefile.html'
	form_class = ChooseFileForm

	def form_valid(self, form):
		self.filename=form.cleaned_data['filename']
		self.bank=form.cleaned_data['bank']
		return super().form_valid(form)

	def get_success_url(self, **kwargs):
		return reverse('transaction-import', kwargs={'bank':self.bank,'filename':self.filename})

#Import File Formset FormView
class TransactionImportView(FormView):
	template_name = 'transaction_import.html'
	success_url = '/'
	form_class = TransactionFormSet

	def get_initial(self):
	
		initial=super(TransactionImportView, self).get_initial()
		filename=self.kwargs['filename']
		bank=self.kwargs['bank']
		
		with open(filename) as csvfile:
			if bank == 'PC':
				next(csvfile)
			readCSV = csv.reader(csvfile, delimiter=',')

			data_list=[]
			
			try:
				no_cat = Category.objects.get(name='None') #Needs to be setup ahead or will fail
			except Category.DoesNotExist:
				fail # Also need to create a group, not best solution
	
			#Import Data from CSV file
			#Format is for TD or President's Choice
			for row in readCSV:
				if bank=='TD':
					date=datetime.datetime.strptime(row[0], '%m/%d/%Y').date()
					description=row[1].strip()
					if row[2]:
						amount=Decimal(row[2].replace(',',''))
						amount=amount*-1
					if row[3]:
						amount=Decimal(row[3].replace(',',''))
				if bank=='PC':
					date=datetime.datetime.strptime(row[3], '%m/%d/%Y').date()
					description=row[0].strip()
					amount=Decimal(row[5])
					
				#Looks for duplicate imports, does not import
				duplicate=Transaction.objects.filter(
					description=description,
					date=date,
					amount=amount,
					)
				if not duplicate:
					#Looks for older matching transactions so can apply category
					t=Transaction.objects.filter(description=description)
					if t:
						#Looks for saved transactions so can apply saved category
						#This catches transactions with the same name but different amount, Condo Fees
						st=SavedTransaction.objects.filter(description=description, amount=amount)
						if st:
							category=st[0].category
						else:
							category=t[0].category
					else:
						#Looks for saved bank transfers
						#For E-Transfers, strips back to the ***
						description = description[:-3]					
						st=SavedTransaction.objects.filter(description=description, amount=amount)
						if st:
							category=st[0].category
						else:
							category=no_cat
					data_list.append([date,description,amount,category])

		#Initial data from import for Form
		initial=[{'date': d, 'description':desc, 'amount':a, 'category':c} for d, desc, a, c in data_list ]

		return initial

	def form_valid(self, formset):
		for form in formset:
			t=form.save(commit=False)
			scdt=ScheduledTransaction.objects.filter(description=t.description, amount=t.amount, category=t.category)
			if not scdt:
				#Looks for saved bank transfers
				#For E-Transfers, strips back to the ***
				description=t.description[:-3]
				scdt=ScheduledTransaction.objects.filter(description=description, amount=t.amount)
			if scdt:
				if scdt[0].repeat_every=='SM':
					next_date=scdt[0].scheduled_date+relativedelta(months=+1)
					#Is it a weekend then find the next monday
					if next_date.weekday() > 4:
						next_date=next_date+relativedelta(months=+1, weekday=MO)

					#Check for holiday
					while (next_date.month,next_date.day) in HOLIDAY:
						next_date=next_date+relativedelta(days=+1)
						#Check if new date is a weekend
						if next_date.weekday() > 4:
							next_date=next_date+relativedelta(days=+1, weekday=MO)
							
					
					scdt[0].scheduled_date=next_date
				#scdt[0].save()
		return super().form_valid(form)