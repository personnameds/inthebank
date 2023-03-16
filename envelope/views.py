from django.views.generic.base import TemplateView
from datetime import date
from calendar import monthrange
from category.models import Category, CategoryGroup
from .models import Envelope
from budget.views import get_budget, get_scheduledbudget
from transaction.models import Transaction
from django.views.generic.edit import UpdateView, CreateView
from django.urls import reverse
from django.shortcuts import redirect
from inthebank.views import view_title_context_data
from django.db.models import Sum

def get_month_budget(budget_method):
    pass
    return None

class EnvelopeView(TemplateView):
    template_name='envelope.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        view_title='Envelope for'
        view_url='envelope-list'	
        context, view_date=view_title_context_data(self, context, view_url, view_title)     

        from_date = view_date.replace(day=1)
        to_date = view_date.replace(day=monthrange(view_date.year,view_date.month)[1])

        today = date.today()
        if today.month == view_date.month and today.year == view_date.year:
            context['current'] = True
        else:
            context['current'] = False

        transaction_list = Transaction.objects.filter(date__gte=from_date,date__lte=to_date)
        envelope_list = Envelope.objects.filter(date__gte=from_date,date__lte=to_date)

        total = [0]*2

##Start of Income
        income_category = Category.objects.get(name='TDSB')       
        
        #Income Earned
        earned = transaction_list.filter(category=income_category).aggregate(Sum('amount'))
        earned = earned['amount__sum'] or 0

        #Income Schedule to Earn
        to_earn = get_scheduledbudget(None, income_category,view_date)

        #Income Envelope
        income_envelope = envelope_list.filter(category=income_category)
        if income_envelope:
            income_envelope = income_envelope[0]
            total[1] = income_envelope.amount #If Envelope use in total
        else:
            income_envelope = None
            total[1] = to_earn #If no Envelope use Scheduled

        income_list=(income_category, earned, to_earn, income_envelope)
        
        total[0]=earned

        context['income_list'] = income_list
## End of Income

        full_list=[]
        group_list = CategoryGroup.objects.all().exclude(name='Credit Cards').exclude(name='Income')

        for group in group_list:
            categories = group.category_set.all()
            category_list=[]

            #Group Budget
            group_budget = get_budget(group,None,group.budget_method,view_date)

            #Group Envelope
            group_envelope = envelope_list.filter(categorygroup=group)
            if group_envelope:
                group_envelope = group_envelope[0]
                total[1] = total[1] + group_envelope.amount
            else:
                group_envelope = None
                if group_budget:
                    total[1] = total[1] + group_budget


            #Group Spent
            group_spent = transaction_list.filter(category__in=categories,date__gte=from_date,date__lte=to_date).aggregate(Sum('amount'))
            group_spent = group_spent['amount__sum'] or 0      

            total[0] = total[0] + group_spent

			#Category Spent
            for category in categories:
                category_spent = transaction_list.filter(category=category,date__gte=from_date,date__lte=to_date).aggregate(Sum('amount'))
                category_spent = category_spent['amount__sum'] or 0

                #Category Budget
                category_budget = get_budget(None,category,category.budget_method,view_date)
                
                #Category Envelope
                category_envelope = envelope_list.filter(category=category)
                if category_envelope:
                    category_envelope = category_envelope[0]
                    total[1] = total[1] + category_envelope.amount
                else:
                    category_envelope = None
                    if category_budget:
                        total[1] = total[1] + category_budget


				#Crategory List
                category_list.append((category,category_spent,category_budget,category_envelope))

            full_list.append(((group,group_spent,group_budget,group_envelope),category_list))

        context['full_list'] = full_list
        context['total'] = total
        return context

class EnvelopeUpdateView(UpdateView):
    model  = Envelope
    template_name = 'envelope_update_form.html'
    fields=['amount',]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.categorygroup:
            group = self.object.categorygroup
            context['group'] = group
        else:
            category = self.object.category
            context['category'] = category
        return context

    def form_valid(self, form):
        submit = self.request.POST.get('submit')
        if submit == 'Delete':            
            envelope = Envelope.objects.get(pk=self.kwargs['pk'])
            envelope.delete()
            return redirect('envelope-list')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('envelope-list')

class EnvelopeCreateView(CreateView):
    model  = Envelope
    template_name = 'envelope_form.html'
    fields=['amount',]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs['group_pk'] != 'None':
            group = CategoryGroup.objects.get(pk=self.kwargs['group_pk'])
        else:
            category = Category.objects.get(pk=self.kwargs['cat_pk'])
            group = category.group
            context['category'] = category
        
        context['group'] = group
        return context

    def form_valid(self, form):
        if self.kwargs['group_pk'] != 'None':
            group = CategoryGroup.objects.get(pk=self.kwargs['group_pk'])
            form.instance.categorygroup = group
        else:
            cat = Category.objects.get(pk=self.kwargs['cat_pk'])
            form.instance.category = cat

        today = date.today()
        form.instance.date = today
        
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse('envelope-list')