from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from ipware import get_client_ip
from .models import Poll, Choice
from django.views.generic import DetailView, ListView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import PollCreateForm, ChoiceCreateForm
from django.contrib.auth import login, logout
from django.db.models import Q


import uuid

public_user = User.objects.filter(username='public').first()

def error_404_view(request, exception):
    return render(request,'polls/home.html')

def error_500_view(request):
    return redirect('home')

def get_ip_address(request):
    ip = None
    try:
        ip, is_routable = get_client_ip(request)
    except:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    return str(ip).replace('.','_')+'@anonyuser'
# Create your views here.
def home(request):

    return render(request,'polls/home.html',{"title":'Home'})


class UserPollListView(LoginRequiredMixin,ListView):
    model = Poll
    template_name = 'poll/poll_list.html'
    context_object_name = 'polls'
    paginate_by = 5


    def get_queryset(self):
        user = get_object_or_404(User, username = self.kwargs.get('username'))
        search_title = self.request.GET.get('search_title')

        polls = None
        if search_title is None:
             polls = Poll.objects.filter(author = user).order_by('-time_posted')
        else:
            polls = Poll.objects.filter(
                Q(title__icontains=search_title) & Q(author = user)
                ).order_by('-time_posted')
        return polls


        
class PollDeleteView(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    model = Poll
    success_message = "Poll has been deleted successfully"
    success_url='/'
    template_name = 'polls/poll_delete.html'

    def test_func(self):
        poll = self.get_object()
        if self.request.user == poll.author:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message )
        return super(PollDeleteView, self).delete(request, *args, **kwargs)

def add_poll(request):
    if request.user.is_anonymous:
        current_user = public_user
    else:
        current_user = request.user

    if request.method == 'POST':
        submit_counter = request.POST['submit_counter']
        p_form = PollCreateForm(request.POST,request.FILES, instance=Poll())
        n_Choice = int(request.POST['counter'])
        c_form = [ChoiceCreateForm(request.POST,request.FILES, prefix = str(x), instance=Choice()) for x in range(0,n_Choice)]
        
        if submit_counter == 'submit':
            #Submit the form 
            

            if p_form.is_valid() and all([cf.is_valid() for cf in c_form]):
                new_poll = p_form.save(commit=False)
                new_poll.author = current_user
                poll_link = uuid.uuid1().hex[0:9]
                new_poll.link = poll_link
                new_poll.save()
                for cf in c_form:
                    new_choice = cf.save(commit=False)
                    new_choice.poll = new_poll
                    new_choice.save()
                messages.success(request, f'You have successfuly created a poll')
                return redirect('poll-detail', link = poll_link)
                
        elif submit_counter == 'add':

            #Add one field
            c_form.append(ChoiceCreateForm( prefix = n_Choice, instance=Choice()))
            n_Choice = n_Choice + 1
        elif submit_counter == 'subtract':
            if n_Choice > 2:
                c_form = c_form[:-1]
                n_Choice = n_Choice - 1
            else:
                messages.warning(request, "Minimum 2 fields are mandatory for a poll!")

        context = {
            'p_form':p_form,
            'c_form':c_form,
            'counter':n_Choice,
            'submit_counter': 'submit'
            }
        return render(request, 'polls/poll_form.html',context)

    else:
        n_Choice = 2
        p_form = PollCreateForm(instance=Poll())
        c_form = [ChoiceCreateForm( prefix = str(x), instance=Choice()) for x in range(0,n_Choice)]
        ''' We need atleast 2 Choice for a poll '''
    context = {
        'p_form':p_form,
        'c_form':c_form,
        'counter':n_Choice,
        'submit_counter':'submit'
    }
    return render(request, 'polls/poll_form.html',context)

def poll_detail(request, link='new'):
    is_fake = False
    voters = None
    if request.user.is_anonymous:
        create_fake_user(request, username= get_ip_address(request))
        is_fake = True

    try:
        voters =   Poll.objects.get(link=link).voters.all()
    except:
        voters = None

    if request.method == 'POST':
        if voters is None or  (voters is not None and  request.user not in voters):
            option = Poll.objects.get(link=link).choice_set.get(id=int(request.POST["choice"]))
            option.choice_count= option.choice_count + 1
            Poll.objects.get(link=link).voters.add(request.user)
            option.save()
            if is_fake:
                logout(request)
            return redirect('poll-result', link)
    else:
        if voters is not None:
            if request.user in voters:
                messages.warning(request, 'You have already voted')
                if is_fake:
                    logout(request)
                return redirect('poll-result', link)
        context={
            "poll": Poll.objects.get(link=link),
            "choices": Poll.objects.get(link=link).choice_set.all()
        }
        if is_fake:
                logout(request)
        return render(request, 'polls/poll_detail.html',context)


def result(request, link='new'):
    if link =='poll/result':
        return redirect('poll-create')
    labels = []
    data = []
    queryset = Poll.objects.get(link= link).choice_set.order_by('-choice_count')
    empty_poll_flag = True
    for choice in queryset:
        labels.append(choice.choice_text)
        if int(choice.choice_count) != 0:
            empty_poll_flag = False
        data.append(choice.choice_count)
    if empty_poll_flag:
        labels.append("Empty")
        data.append(1)
    context = {
        'poll':Poll.objects.get(link= link),
        'labels': labels,
        'data': data,
    }
    return  render(request, 'polls/poll_result.html',context)

        
def create_fake_user(request, username):
    # request.session.save()
    # username = str(request.session.session_key) + '@anonyvoter'
    try:
        user = User.objects.create_user(username)
    except:
        user = User.objects.get(username=username)
    login(request, user)