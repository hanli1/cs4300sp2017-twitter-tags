from django.conf.urls import url

from . import views

app_name = 'pt'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajax/get_users_handles/$', views.get_users_handles, name='get_users_handles')
]