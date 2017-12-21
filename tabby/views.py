from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Tuser, Question

def index(request):
    question = {
        'votes': '2333', 'answers': '10', 'author': 'carl', 'time': '1h ago',
        'title': 'some title', 'tags': ['tag1', 'tag2']}
    test = [question, question]
    return render(request, 'tabby/index.html', {'q_list': test})

def login(request):
    if request.method == 'POST':
        name = request.POST.get('user', None)
        password = request.POST.get('password', None)
        user = authenticate(username=name, password=password)
        if user is not None:
            auth.login(request, user)
            question_list = user.tuser.question_set.all()
            q_name_list = []
            for question in question_list:
                q_name_list.append(question.title)
            return render(request, 'tabby/profile.html', {'questions': q_name_list})
        else:
            return render(request, 'tabby/error.html', {'err_msg': 'incorrect username or password.'})
    else:
        return render(request, 'tabby/error.html', {'err_msg': 'method should be POST?'})

def register(request):
    if request.method == 'POST':
        name = request.POST.get('user', None)
        password = request.POST.get('password', None)
        email = request.POST.get('email', None)
        user = authenticate(username=name, password=password)
        if user is None:
            new_user = User.objects.create_user(name, email, password)
            new_tuser = Tuser(user=new_user, status=0)
            new_tuser.save()
            return render(request, 'tabby/profile.html', {})
        else:
            return render(request, 'tabby/userExist.html', {})

def newQuestion(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            title = request.POST.get('title', None)
            category = request.POST.get('category', None)
            description = request.POST.get('description', None)
            put_time = timezone.now()
            tuser = request.user.tuser
            new_q = Question(tuser=tuser, title=title, category=category, description=description, put_time=put_time)
            new_q.save()
            return render(request, 'tabby/profile.html', {})
        else:
            return render(request, 'tabby/error.html', {'err_msg': 'not login...'})
    else:
        return render(request, 'tabby/new_question.html', {})
