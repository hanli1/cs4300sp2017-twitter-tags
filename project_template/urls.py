from django.conf.urls import url

from . import views

app_name = 'pt'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^api/get_users_handles', views.get_users_handles, name='get_users_handles'),
    url(r'^api/get_tag_labels', views.get_tag_labels, name='get_tag_labels'),
    url(r'^api/search', views.search, name='search'),
    url(r'^api/get_user_info', views.get_user_info, name='get_user_info')
]