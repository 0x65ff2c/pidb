from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseRedirect
from .models import *
from django.db.models import *
from django.conf import settings
import datetime
import os

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

def topKCategory(K):
    return [x.name for x in Category.objects.all().order_by('-popularity')[:K]]

@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')

def login(request):
    if request.method == 'POST':
        next_url = request.POST.get('next_url', '/')
        name = request.POST.get('user', None)
        password = request.POST.get('password', None)
        user = authenticate(username=name, password=password)
        if user is not None:
            auth.login(request, user)
            question_list = user.tuser.question_set.all()
            q_name_list = []
            for question in question_list:
                q_name_list.append(question.title)
            return redirect(next_url)
        else:
            return render(request, 'tabby/error.html', {'err_msg': 'incorrect username or password.'})
    else:
        next_url = request.GET.get('next', '/')
        return render(request, 'tabby/login.html', {'next_url': next_url})

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
            return render(request, 'tabby/error.html', {'err_msg': 'user exist'})

@login_required
def newQuestion(request):
    """
    to make things easier, the browser tends to get tag name instead of tag id
    """
    if request.method == 'POST':
        title = request.POST.get('title', None)
        tags = request.POST.get('tags', None)
        tag_list = tags.split(',')
        tag_id_list = []
        for tag in tag_list:
            tag_id_list.append(str(Category.objects.get(name=tag).id))
        category = ','.join(tag_id_list)
        description = request.POST.get('description', None)
        put_time = timezone.now()
        tuser = request.user.tuser
        new_q = Question(tuser=tuser, title=title, category=category, description=description, put_time=put_time)
        new_q.save()
        for tag in tag_list:
            label = Category.objects.all().get(name=tag)
            label.popularity += 1
            label.save()
        return redirect('/')
    else:
        all_taglist = [x.name for x in Category.objects.all()]
        default_taglist = topKCategory(20)
        return render(request, 'tabby/new_question.html',
            {'is_authenticated': True,
            'default_taglist': default_taglist,
            'all_taglist': all_taglist})

def newAnswer(request):
    if request.method == 'POST':
        q_id = request.POST.get('q_id', None)
        description = request.POST.get('ans', None)
        reply = Reply(put_time=timezone.now(), thumb_up=0, description=description, question=Question.objects.all().get(pk=q_id), tuser=request.user.tuser)
        reply.save()
        tags = Question.objects.all().get(pk=q_id).category.split(',')
        for tag in tags:
            label = Category.objects.all().get(pk=int(tag))
            label.popularity += 1
            label.save()
        return HttpResponse()		
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
        # cur_user_vote: whether current user has voted for this answer
        # 0 no
        # 2 like
        # 4 hate
        if is_authenticated:
            try:
                vote_relation = request.user.tuser.thumbrelation_set.get(reply=ans)
                cur_user_vote = 2 if vote_relation.thumb_flag else 4
            except:
                cur_user_vote = 0
        else:
            cur_user_vote = 0
        ans_info = {
            'id': ans.id,
            'time_diff': time_diff,
            'description': ans.description,
            'author': ans.tuser.user.username,
            'head_image': ans.tuser.headimg.name if ans.tuser.headimg.name is not None else 'img/default.png',
            'votes': ans.thumb_up,
            'cur_user_vote': cur_user_vote
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
        order = request.GET.get('order', 0)
        is_authenticated = True if request.user.is_authenticated else False
        q_list = []
        for question in Question.objects.all():
            q_dict = {}
            q_dict['title'] = question.title
            q_dict['tags'] = [Category.objects.all().get(pk=x).name for x in question.category.strip().split(',')]
            related_reply = question.reply_set.all()
            q_dict['reply_num'] = related_reply.count()
            q_dict.update(related_reply.aggregate(total_thumb = Sum('thumb_up')))
            if q_dict['total_thumb'] is None:
                q_dict['total_thumb'] = 0
            q_dict['id'] = question.id
            if related_reply.count() > 0:
                q_dict['latest_act_user'] = related_reply.order_by('-put_time')[0].tuser.user.username
                q_dict['latest_act_time'] = getTimeDiff(related_reply.order_by('-put_time')[0].put_time, timezone.now())
                q_dict['lat'] = related_reply.order_by('-put_time')[0].put_time
                q_dict['latest_act_type'] = 'replied'
            else:
                q_dict['latest_act_user'] = question.tuser.user.username
                q_dict['latest_act_time'] = getTimeDiff(question.put_time, timezone.now())
                q_dict['lat'] = question.put_time
                q_dict['latest_act_type'] = 'asked'
            q_list.append(q_dict)
        order = int(order)
        if order == 0:
            q_list = sorted(q_list, key=lambda x: x['lat'], reverse=True)
        elif order == 1:
            q_list = sorted(q_list, key=lambda x: x['reply_num'], reverse=True)
        else:
            q_list = sorted(q_list, key=lambda x: x['total_thumb'], reverse=True)
        return render(request, 'tabby/home.html',
            {'q_list': q_list,
            'is_authenticated': is_authenticated,
            'order': order})
    else:
        pass	

def profile(request, user_name):
    try:
        user = User.objects.all().get(username=user_name).tuser
    except:
        return render(request, 'tabby/profile.html', {'err_msg': 'No such user!'})
    if request.method == 'GET':
        q_list = []
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
            reply_set = question.reply_set.all()
            question_info['top_answer'] = reply_set.order_by('-thumb_up')[0].description if reply_set.count() > 0 else None
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
        head_image_name = 'img/default.png' if user.headimg.name is None else user.headimg.name
        return render(request, 'tabby/profile.html', {'user_name': user.user.username, 'user_latest_action': q_list, 'head_image': head_image_name})
    else:
        user.headimg = request.FILES['head_image']
        user.headimg.name = user.user.username + '_' + str(timezone.now()) + '.jpg'
        user.save()
        return redirect(request.path)

@login_required
def vote(request):
    if request.method == 'POST':
        vote_type = int(request.POST.get('vote_type', None))
        ans_id = request.POST.get('ans_id', None)
        cur_ans = Reply.objects.get(id=ans_id)
        try:
            vote_relation = request.user.tuser.thumbrelation_set.get(reply=Reply.objects.get(id=int(ans_id)))
            old_flag = vote_relation.thumb_flag
            if vote_type == 0:
                vote_relation.delete()
                cur_ans.thumb_up = cur_ans.thumb_up - 1 if old_flag else cur_ans.thumb_up + 1
            else:
                vote_relation.thumb_flag = True if vote_type == 2 else False
                if old_flag != vote_relation.thumb_flag:
                    cur_ans.thumb_up = cur_ans.thumb_up - 2 if old_flag else cur_ans.thumb_up + 2
                vote_relation.save()
        except:
            if vote_type != 0:
                tem_relation = ThumbRelation(
                    reply=Reply.objects.get(id=int(ans_id)),
                    tuser=request.user.tuser,
                    thumb_flag=True if vote_type == 2 else False)
                tem_relation.save()
                cur_ans.thumb_up = cur_ans.thumb_up + 1 if tem_relation.thumb_flag else cur_ans.thumb_up - 1
        cur_ans.save()
        return HttpResponse(cur_ans.thumb_up)
    else:
        pass

def search(request):
    return render(request, 'tabby/search.html', {})
