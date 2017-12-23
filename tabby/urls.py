from django.conf.urls import url
from . import views

app_name = 'tabby'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^new_question/$', views.newQuestion, name='new_question'),
    url(r'^new_answer/$', views.newAnswer, name='new_answer'),
    url(r'^question/([0-9]+)/$', views.question, name='question'),
    url(r'^vote/$', views.vote, name='vote')
]
