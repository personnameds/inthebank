from django.views.generic.base import TemplateView
from datetime import date
from category.models import Category, CategoryGroup
from budget.views import get_spent, get_month_scheduledbudget, get_month_avgquarterbudget, get_month_constantbudget, get_month_lastyearbudget
from .models import Envelope
from dateutil.relativedelta import relativedelta
from django.views.generic.edit import UpdateView, CreateView
from django.urls import reverse

class EnvelopeView(TemplateView):
    template_name='envelope.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        today = date.today()
        

##Viewing Date (Currently has a Hard Stop of January 2023)
        if self.kwargs:
            view_date = date(self.kwargs['year'],self.kwargs['month'],1)
        else:
            view_date = today
        last_month = view_date + relativedelta(months=-1)
        
        if view_date.year >= 2023 and view_date.month > 1:
            view_date = date(view_date.year,view_date.month,1)
            prev = view_date + relativedelta(months=-1)
        elif view_date.year == 2023 and view_date.month == 1:
            prev = None
        if view_date.year == today.year and view_date.month == today.month:
            next = None
        else:
            next = view_date + relativedelta(months=+1)

        context['view_date'] = view_date
        context['prev'] = prev
        context['next'] = next

##Start of Income
        income_category = Category.objects.get(name='TDSB')       
        earned = get_spent(None, income_category, view_date)
        if view_date.month == today.month: #Doesn't work for past month, defaults to 0
            to_earn = get_month_scheduledbudget(None, income_category, view_date)
        else:
            to_earn = 0
        total = [0] * 5
        total[0] = earned
        total[1] = to_earn
        
        try: 
            carryover = Envelope.objects.get(category=income_category, date__month=last_month.month, date__year=last_month.year).carryover
        except Envelope.DoesNotExist:
            carryover = 0        

        try:
            income_envelope = Envelope.objects.get(category=income_category, date__month=view_date.month, date__year=view_date.year)  
            plus_minus = earned - income_envelope.amount
            if earned != 0:
                carryover += plus_minus
            else:
                carryover = carryover
            income_envelope.date = view_date
            income_envelope.plus_minus = plus_minus
            income_envelope.carryover = carryover
            income_envelope.save()

        except Envelope.DoesNotExist:
            plus_minus = earned - to_earn
            if earned != 0:
                carryover += plus_minus            
            else:
                carryover = carryover
            income_envelope = Envelope(
                category = income_category,
                categorygroup = income_category.group,
                amount = to_earn,
                plus_minus = plus_minus,
                carryover = carryover,
                date = view_date,
                )
            income_envelope.save()

        total[2] = income_envelope.amount
        total[3] = plus_minus
        total[4] = carryover

        income_list=(income_category, earned, to_earn, income_envelope)

## End of Income

## Categories
# Category Groups
        category_groups=CategoryGroup.objects.all().exclude(name='Income').exclude(name='Credit Cards').exclude(name='None')
        spent_list=[]

        for category_group in category_groups:                      
            #List of categories in the group
            categories = Category.objects.filter(group=category_group)
            group_spent = get_spent(categories, None, view_date)
            total[0] += group_spent
            
            try: 
                carryover = Envelope.objects.get(categorygroup=category_group, date__month=last_month.month, date__year=last_month.year).carryover
            except Envelope.DoesNotExist:
                carryover = 0        

            #Group Budget
            if category_group.budget_method != 'N':
			    #Constant
                if category_group.budget_method == 'C':
                    month_budget = get_month_constantbudget(category_group,None)
			    #Avg over Quarter
                elif category_group.budget_method == 'A':
                    month_budget = get_month_avgquarterbudget(categories, None, view_date)
                #Scheduled
                elif category_group.budget_method == 'S': #Doesn't work for past month, defaults to 0
                    if view_date.month == today.month:
                        month_budget = get_month_scheduledbudget(category_group, None,view_date)
                    else:
                        month_budget = 0
			    #Last Year
                elif category_group.budget_method == 'Y':
                    month_budget = get_month_lastyearbudget(categories, None, view_date)
                total[1] += month_budget
            else:
                month_budget = None
                plus_minus = 0    

            try:
                group_envelope = Envelope.objects.get(categorygroup=category_group, date__month=view_date.month, date__year=view_date.year)  
                amount = group_envelope.amount
                plus_minus = group_spent - amount
                if group_spent != 0:
                    carryover += plus_minus
                else:
                    carryover = carryover
                group_envelope.plus_minus = plus_minus
                group_envelope.carryover = carryover
                group_envelope.date = view_date
                group_envelope.save()

            except Envelope.DoesNotExist:
                if month_budget or carryover > 0:
                    plus_minus = group_spent - month_budget
                    if group_spent != 0:
                        carryover += plus_minus
                    else:
                        carryover = carryover
                    amount = month_budget  
                    group_envelope = Envelope(
                        categorygroup = category_group,
                        amount = amount,
                        plus_minus = plus_minus,
                        carryover = carryover,
                        date = view_date,
                        )
                    group_envelope.save()

                else:
                    group_envelope = None
                    amount = 0
                    plus_minus = 0
                            
            total[2] += amount
            total[3] += plus_minus
            total[4] += carryover

            category_group_list = ((category_group, group_spent, month_budget, group_envelope))
            categories_list = []

            #Each Category in the group
            for category in categories:
                spent = get_spent(None, category, view_date)	
                group_spent += spent
                total[0] += spent

                try: 
                    carryover = Envelope.objects.get(category=category, date__month=last_month.month, date__year=last_month.year).carryover
                except Envelope.DoesNotExist:
                    carryover = 0        

                #Category Budget
                if category.budget_method != 'N':
    			    #Constant
                    if category.budget_method == 'C':
                        month_budget = get_month_constantbudget(None, category)
			        #Avg over Quarter
                    elif category.budget_method == 'A':
                        month_budget = get_month_avgquarterbudget(None, category, view_date)
                    #Scheduled
                    elif category.budget_method == 'S': #Doesn't work for past month, defaults to 0
                        if view_date.month == today.month:
                            month_budget = get_month_scheduledbudget(None, category, view_date)
                        else:
                            month_budget = 0
			        #Last Year
                    elif category.budget_method == 'Y':
                        month_budget = get_month_lastyearbudget(None, category, view_date)
                    total[1] += month_budget
                else:
                    month_budget = None
                    plus_minus = 0
			
                try:
                    category_envelope = Envelope.objects.get(category=category, date__month=view_date.month, date__year=view_date.year)  
                    amount = category_envelope.amount
                    plus_minus = spent - amount
                    if spent != 0:
                        carryover += plus_minus
                    else:
                        carryover == carryover
                    category_envelope.plus_minus = plus_minus
                    category_envelope.carryover = carryover
                    category_envelope.date = view_date
                    category_envelope.save()

                except Envelope.DoesNotExist:
                    if month_budget or carryover > 0:
                        amount = month_budget
                        plus_minus = spent - month_budget
                        if spent != 0:
                            carryover += plus_minus            
                        else:
                            carryover = carryover
                        category_envelope = Envelope(
                            category = category,
                            amount = amount,
                            plus_minus = plus_minus,
                            carryover = carryover,
                            date = view_date,
                            )
                        category_envelope.save()
                    else:
                        category_envelope = None
                        amount = 0
                        plus_minus = 0

                total[2] += amount
                total[3] += plus_minus
                total[4] += carryover
                
                categories_list.append((category, spent, month_budget, category_envelope))

            spent_list.append((category_group_list, categories_list))


        context['income_list'] = income_list
        context['spent_list'] = spent_list
        context['total'] = total

        return context

class EnvelopeUpdateView(UpdateView):
	model  = Envelope
	template_name = 'generic_update_form.html'
	fields=['amount',]
	
	def get_success_url(self):
		return reverse('envelope-list')

class EnvelopeCreateView(CreateView):
    model  = Envelope
    template_name = 'envelope_form.html'
    fields=['amount',]

    def form_valid(self, form):
        if self.kwargs['group_pk'] != 'None':
            group = CategoryGroup.objects.get(pk=self.kwargs['group_pk'])
            form.instance.categorygroup = group
        else:
            cat = Category.objects.get(pk=self.kwargs['cat_pk'])
            form.instance.category = cat
        
        today = date.today()
        form.instance.date = today
        form.instance.plus_minus = 0
        form.instance.carryover = 0
        
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse('envelope-list')