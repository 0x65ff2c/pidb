from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponseRedirect
from .models import *
from django.db.models import *
import datetime

def getTimeDiff(startTime, endTime):
	
	''' returns a string respresenting the difference. eg. "2 days ago""37 minutes ago" '''	
	
	diff = endTime - startTime
	if diff.days >= 1:
		return '%d day%s ago' % (diff.days, '' if diff.days == 1 else 's')
	if diff.seconds < 60:
		return '%d second%s ago' % (diff.seconds, '' if diff.seconds == 1 else 's')
	if diff.seconds < 3600:
		minutes = int(diff.seconds / 60)
		return '%d minute%s ago' % (minutes, '' if minutes == 1 else 's')
	
	hours = int(diff.seconds / 3600)
	return '%d hour%s ago' % (hours, '' if hours == 1 else 's')



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
        return render(request, 'tabby/login.html', {})

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

def newAnswer(request):
    if request.method == 'POST':
        q_id = request.POST.get('q_id', None)
        description = request.POST.get('ans', None)
        reply = Reply(put_time=timezone.now(), thumb_up=0, description=description, question=Question.objects.all().get(pk=q_id), tuser=request.user.tuser)
        reply.save()		
        return HttpResponseRedirect('../question/' + str(q_id))
    else:
        return render(request, 'tabby/error.html', {'err_msg': 'method should be Post'})

def question(request, q_id):
    is_authenticated = True if request.user.is_authenticated else False
    try:
        q = Question.objects.get(id=q_id)
        ans_set = q.reply_set.all()
    except:
        return render(request, 'tabby/error.html', {'err_msg': 'question not found'})
    title = q.title
    description = q.description
    tag = q.category
    q_author = q.tuser.user.username
    ans_list = []
    for ans in ans_set:
        time_diff = getTimeDiff(ans.put_time, timezone.now())
        ans_info = {
            'time_diff': time_diff,
            'description': ans.description,
            'author': ans.tuser.user.username,
            'votes': ans.thumb_up
        }
        ans_list.append(ans_info)
    return render(request, 'tabby/question.html', 
        {'is_authenticated': is_authenticated,
        'q_id': q_id,
        'title': title,
        'description': description,
        'tags': [Category.objects.all().get(pk=x).name for x in tag.strip().split(',')],
        'q_author': q_author,
        'ans_list': ans_list})

def home(request):
	if request.method == 'GET':
		q_list = []
		for question in Question.objects.all():
			q_dict = {}
			q_dict['title'] = question.title
			q_dict['category'] = [Category.objects.all().get(pk=x).name for x in question.category.strip().split(',')]
			related_reply = question.reply_set.all()
			q_dict['reply_num'] = related_reply.count()
			q_dict.update(related_reply.aggregate(total_thumb = Sum('thumb_up')))
			if q_dict['total_thumb'] is None:
				q_dict['total_thumb'] = 0
			if related_reply.count() > 0:
				q_dict['latest_act_user'] = related_reply.order_by('-put_time')[0].tuser.user.username
				q_dict['latest_act_time'] = getTimeDiff(related_reply.order_by('-put_time')[0].put_time, timezone.now())
				q_dict['latest_act_type'] = 'reply'
			else:
				q_dict['latest_act_user'] = question.tuser.user.username
				q_dict['latest_act_time'] = getTimeDiff(question.put_time, timezone.now())
				q_dict['latest_act_type'] = 'ask'
			q_list.append(q_dict)

		return render(request, 'tabby/home.html', {'question_info': q_list})
	else:
		pass

def profile(request, username):
	if request.method == 'GET':
		q_list = []
		user = Tuser.objects.all().get(username=username)

		for reply in user.reply_set.all():
			reply_info = {}
			reply_info['reply_id'] = reply.id
			reply_info['reply_content'] = reply.description
			reply_info['question_id'] = reply.question.id
			reply_info['question_title'] = reply.question.title
			reply_info['type'] = 'reply'
			q_list.append(reply_info)

		for question in user.question_set.all():
			question_info = {}
			question_info['question_id'] = question.id
			question_info['question_title'] = question.title
			question_info['top_answer'] = question.reply_set.all().order_by('-thumb_up')[0].description
			question_info['type'] = 'question'
			q_list.append(question_info)

		for thumb_entry in user.thumbrelation_set.all():
			t_info = {}
			related_question = thumb_entry.reply.question
			t_info['question_id'] = related_question.id
			t_info['question_title'] = related_question.title
			t_info['reply_id'] = thumb_entry.reply.id
			t_info['reply_content'] = thumb_entry.reply.description
			t_info['type'] = 'thumb'
			q_list.append(t_info)

		return render(request, 'tabby/profile.html', {'user_latest_action': q_list})
	else:
		pass


