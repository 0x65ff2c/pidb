from django.db import models
from django.contrib.auth.models import User

class Tuser(models.Model):
    user = models.OneToOneField(User)
    status = models.IntegerField(default=0)

class Question(models.Model):
    tuser = models.ForeignKey(Tuser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    description = models.TextField()
    put_time = models.DateTimeField(auto_now_add=True)

class Reply(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    tuser = models.ForeignKey(Tuser, on_delete=models.CASCADE)
    put_time = models.DateTimeField(auto_now_add=True)
    thumb_up = models.IntegerField(default=0)
    description = models.TextField()

class ThumbRelation(models.Model):
	reply = models.ForeignKey(Reply, on_delete=models.CASCADE)
	tuser = models.ForeignKey(Tuser, on_delete=models.CASCADE)
	thumb_flag = models.BooleanField()

class Category(models.Model):
	name = models.CharField(max_length=200)
	popularity = models.IntegerField(default=0)
