from .forms import TransactionFormSet, ChooseFileForm, TransactionForm
from .models import Transaction, ScheduledTransaction, SavedTransaction
from category.models import Category
from account.models import Account
from inthebank.settings import BASE_DIR
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse
from inthebank.views import view_title_context_data
import csv
from io import StringIO
import os
import tempfile

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

#Import Function, enter file name
#Make this a selection window in future
#Only works in home directory
class ChooseFileView(FormView):
	template_name = 'choosefile.html'
	form_class = ChooseFileForm
	
	def form_valid(self, form):
		csvfile = form.cleaned_data['csvfile'].read()
		
		with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tempcsvfile:
			tempcsvfile.write(csvfile)
		self.request.session['tempcsvfile'] = tempcsvfile.name
		return super().form_valid(form)
	
	def get_success_url(self, **kwargs):
		'''
	 	a = self.request.a
		with open(a) as b:
			c = csv.reader(b, delimiter=',')
		os.remove(a)
		'''
		account=self.request.POST['account']
		balance=self.request.POST['balance']
		return reverse('transaction-import', kwargs={'account':account, 'balance':balance})

#Import File Formset FormView
class TransactionImportView(FormView):
	template_name = 'transaction_import.html'
	success_url = '/'
	form_class = TransactionFormSet
	
	def get_initial(self):

		initial=super(TransactionImportView, self).get_initial()
		account=int(self.kwargs['account'])
		balance=Decimal(self.kwargs['balance'])
		tempcsvfile = self.request.session['tempcsvfile']

		data_list=[]
		no_cat = Category.objects.get(name='None') #Needs to be setup ahead or will fail

		with open(tempcsvfile) as csvfile:
			if account == 3:
				next(csvfile)

			readCSV = csv.reader(csvfile, delimiter=',')

			#Import Data from CSV file
			#Format is for TD or President's Choice
			for row in readCSV:
				if account < 3:
					date=datetime.datetime.strptime(row[0], '%m/%d/%Y').date()
					description=row[1].strip()
					if row[2]:
						amount=Decimal(row[2].replace(',',''))
						amount=amount*-1
					if row[3]:
						amount=Decimal(row[3].replace(',',''))
				if account == 3:
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
					category = no_cat
					
					if t:
						#Looks for saved transactions so can apply saved category
						#This catches transactions with the same name but different amount, Condo Fees
						st=SavedTransaction.objects.filter(description=description, amount=amount)
						if st:
							category=st[0].category
						else:
							category=t[0].category
					else:
						#Looks for saved E-Transfers transfers
						#Rent, Music lessons ***
						temp_description = description[:-3]					
						st=SavedTransaction.objects.filter(description=temp_description, amount=amount)
						if st:
							category=st[0].category
						
						#Looks for bank transfer
						#RESP
						temp_description = description[6:]					
						st=SavedTransaction.objects.filter(description=temp_description, amount=amount)
						if st:
							category=st[0].category
						
					data_list.append([date,description,amount,category])
			
				#End For Row


		#Initial data from import for Form
		initial=[{'date': d, 'description':desc, 'amount':a, 'category':c} for d, desc, a, c in data_list ]
		return initial

	def form_valid(self, formset):
		account = Account.objects.get(pk=self.kwargs['account'])
		account.balance = self.kwargs['balance']
		account.save()

		for form in formset:
			t=form.save()
			
			scdt=ScheduledTransaction.objects.filter(description=t.description, category=t.category)
			if scdt:
				next_date=scdt[0].scheduled_date+relativedelta(weeks=+2)
				scdt[0].scheduled_date=next_date
				scdt[0].save()

		return super().form_valid(form)
	

		