from django.conf.urls import url
from . import views

app_name = 'tabby'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^new_question/$', views.newQuestion, name='new_question')
]