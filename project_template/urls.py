from django.conf.urls import url

from . import views

app_name = 'pt'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^ajax/get_users_handles/$', views.get_users_handles, name='get_users_handles'),
    url(r'^ajax/get_tag_labels/$', views.get_tag_labels, name='get_tag_labels'),
    url(r'^ajax/search/$', views.search, name='search')
]